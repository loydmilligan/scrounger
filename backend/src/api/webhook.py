from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import re

from ..database import get_db
from ..models import Lead, RedditMessage, Item

router = APIRouter()


class RedditEmailWebhook(BaseModel):
    """Payload from n8n for Reddit email notifications."""
    from_email: str  # e.g., "Reddit <noreply@redditmail.com>"
    to_email: str
    subject: str  # e.g., "You have a new chat request"
    body: str
    date: Optional[str] = None
    message_id: Optional[str] = None


class WebhookResponse(BaseModel):
    success: bool
    message: str
    lead_id: Optional[int] = None
    reddit_message_id: Optional[int] = None
    lead_created: bool = False
    extracted_message: Optional[str] = None
    duplicate: bool = False


def extract_user_message(body: str, message_type: str) -> str:
    """Extract the actual user message from the email body."""

    if not body:
        return None

    if message_type == "chat_request":
        # Pattern: "u/username wants to chat with you [MESSAGE] View Chat Request"
        match = re.search(r'wants to chat with you\s+(.+?)\s*View Chat Request', body, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    elif message_type in ["post_reply", "comment_reply"]:
        # For post/comment replies, the actual message is at the BEGINNING before the first bullet (•)
        # Examples: "PM • [post title]..." or "Interested in flipper • [post title]..."
        if '•' in body:
            message = body.split('•')[0].strip()
            if message and len(message) > 1:
                return message

        # Fallback: look for content after "ago" timestamp
        match = re.search(r'\d+[smh]?\s*ago\s+(.+?)(?:\s*View Reply|\s*This email)', body, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Fallback: return first meaningful chunk before bullet
    if '•' in body:
        first_part = body.split('•')[0].strip()
        if first_part and len(first_part) > 1:
            return first_part

    return None


def detect_items_mentioned(message: str, db: Session) -> List[Item]:
    """Try to match items mentioned in the message."""
    if not message:
        return []

    items = db.query(Item).filter(Item.status.in_(['listed', 'draft'])).all()
    matched = []

    message_lower = message.lower()

    for item in items:
        # Check if item name or keywords appear in message
        name_words = item.name.lower().split()
        # Match if any significant word from item name appears
        for word in name_words:
            if len(word) > 3 and word in message_lower:
                matched.append(item)
                break

    return matched


@router.post("/reddit-email", response_model=WebhookResponse)
def receive_reddit_email(data: RedditEmailWebhook, db: Session = Depends(get_db)):
    """
    Receive Reddit email notifications from n8n.

    Handles:
    - Chat requests
    - Post replies
    - Comment replies
    - Direct messages

    Auto-creates leads for new users and links to existing items.
    Deduplicates using Gmail message_id.
    """

    # Check for duplicate using Gmail message ID
    if data.message_id:
        existing = db.query(RedditMessage).filter(
            RedditMessage.gmail_message_id == data.message_id
        ).first()
        if existing:
            return WebhookResponse(
                success=True,
                message=f"Duplicate message (already processed as ID {existing.id})",
                lead_id=existing.lead_id,
                reddit_message_id=existing.id,
                duplicate=True
            )

    username = None
    message_type = "unknown"

    # Detect message type and extract username from subject
    subject_lower = data.subject.lower()

    if "chat request" in subject_lower:
        message_type = "chat_request"
        # Username pattern: "u/username wants to chat"
        match = re.search(r'u/(\w+)\s+wants to chat', data.body, re.IGNORECASE)
        if match:
            username = match.group(1)

    elif "replied to your post" in subject_lower:
        message_type = "post_reply"
        # Subject: "u/username replied to your post in r/subreddit"
        match = re.search(r'u/(\w+)\s+replied', data.subject, re.IGNORECASE)
        if match:
            username = match.group(1)

    elif "replied to your comment" in subject_lower:
        message_type = "comment_reply"
        match = re.search(r'u/(\w+)\s+replied', data.subject, re.IGNORECASE)
        if match:
            username = match.group(1)

    elif "new message from" in subject_lower:
        message_type = "direct_message"
        match = re.search(r'from\s+u?/?(\w+)', data.subject, re.IGNORECASE)
        if match:
            username = match.group(1)

    # Fallback username extraction from body
    if not username:
        # Try u/username pattern
        match = re.search(r'u/(\w+)', data.body)
        if match:
            username = match.group(1)

    # Extract the actual user message
    extracted_message = extract_user_message(data.body, message_type)

    # Try to find existing lead or create new one
    lead_id = None
    lead_created = False

    if username and username.lower() not in ['mateo24', 'automoderator', 'deleted']:
        lead = db.query(Lead).filter(
            Lead.username.ilike(username),
            Lead.platform == "reddit"
        ).order_by(Lead.updated_at.desc()).first()

        if lead:
            lead_id = lead.id
            # Update lead's last contact time
            lead.last_contact_at = datetime.utcnow()

            # Add the actual message to notes
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            note_addition = f"\n[{timestamp}] {message_type.upper()}: {extracted_message or data.subject}"
            if lead.notes:
                lead.notes += note_addition
            else:
                lead.notes = note_addition.strip()
        else:
            # Auto-create lead for new user
            # Try to match mentioned items
            matched_items = detect_items_mentioned(extracted_message or data.body, db)
            item_id = matched_items[0].id if matched_items else None

            # If no item matched, use the most recently listed item
            if not item_id:
                recent_item = db.query(Item).filter(
                    Item.status == 'listed'
                ).order_by(Item.listed_at.desc()).first()
                if recent_item:
                    item_id = recent_item.id

            if item_id:
                new_lead = Lead(
                    item_id=item_id,
                    username=username,
                    platform="reddit",
                    contact_method="reddit_dm",
                    status="new",
                    source=f"Email: {data.subject}",
                    notes=f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] AUTO-CREATED from email\n{message_type.upper()}: {extracted_message or 'No message extracted'}"
                )
                db.add(new_lead)
                db.flush()
                lead_id = new_lead.id
                lead_created = True

    # Parse date
    email_date = None
    if data.date:
        try:
            # Handle various date formats
            date_str = data.date.replace('Z', '+00:00')
            email_date = datetime.fromisoformat(date_str)
        except:
            try:
                # Try parsing common email date format
                email_date = datetime.strptime(data.date, '%a, %d %b %Y %H:%M:%S %z')
            except:
                pass

    # Create Reddit message record with full body and Gmail ID for deduplication
    reddit_msg = RedditMessage(
        lead_id=lead_id,
        gmail_message_id=data.message_id,  # For deduplication
        from_user=username or "unknown",
        subject=data.subject,
        body=data.body,  # Store full body
        message_type=message_type,
        extracted_message=extracted_message,  # Store the extracted user message
        email_date=email_date,
        email_from=data.from_email,
        email_subject=data.subject
    )
    db.add(reddit_msg)
    db.commit()
    db.refresh(reddit_msg)

    return WebhookResponse(
        success=True,
        message=f"Processed {message_type} from {username or 'unknown user'}",
        lead_id=lead_id,
        reddit_message_id=reddit_msg.id,
        lead_created=lead_created,
        extracted_message=extracted_message
    )


@router.get("/reddit-messages")
def list_reddit_messages(
    lead_id: Optional[int] = None,
    is_read: Optional[bool] = None,
    username: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List Reddit messages with extracted content."""
    query = db.query(RedditMessage)

    if lead_id:
        query = query.filter(RedditMessage.lead_id == lead_id)
    if is_read is not None:
        query = query.filter(RedditMessage.is_read == is_read)
    if username:
        query = query.filter(RedditMessage.from_user.ilike(f"%{username}%"))

    query = query.order_by(RedditMessage.created_at.desc())

    total = query.count()
    messages = query.offset(skip).limit(limit).all()

    result = []
    for m in messages:
        # Use stored extracted_message, or compute if not stored
        extracted = m.extracted_message
        if not extracted and m.body:
            extracted = extract_user_message(m.body, m.message_type)

        result.append({
            "id": m.id,
            "lead_id": m.lead_id,
            "gmail_message_id": m.gmail_message_id,
            "from_user": m.from_user,
            "subject": m.subject,
            "extracted_message": extracted,
            "full_body": m.body,
            "message_type": m.message_type,
            "is_read": m.is_read,
            "is_replied": m.is_replied,
            "email_date": m.email_date,
            "created_at": m.created_at
        })

    return {
        "messages": result,
        "total": total
    }


@router.patch("/reddit-messages/{message_id}")
def update_reddit_message(
    message_id: int,
    is_read: Optional[bool] = None,
    is_replied: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Mark a Reddit message as read or replied."""
    msg = db.query(RedditMessage).filter(RedditMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    if is_read is not None:
        msg.is_read = is_read
    if is_replied is not None:
        msg.is_replied = is_replied

    db.commit()
    return {"success": True, "message_id": message_id}


@router.post("/reddit-messages/mark-all-read")
def mark_all_read(db: Session = Depends(get_db)):
    """Mark all unread messages as read."""
    count = db.query(RedditMessage).filter(RedditMessage.is_read == False).update({"is_read": True})
    db.commit()
    return {"success": True, "marked_read": count}
