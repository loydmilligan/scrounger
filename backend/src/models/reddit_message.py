from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from datetime import datetime
from ..database import Base


class RedditMessage(Base):
    __tablename__ = "reddit_messages"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)

    # Gmail message ID for deduplication
    gmail_message_id = Column(String(255), unique=True, nullable=True, index=True)

    # Message details
    from_user = Column(String(255), nullable=False)
    subject = Column(String(500))
    body = Column(Text)
    message_type = Column(String(50))  # chat_request, direct_message, post_reply, comment_reply
    extracted_message = Column(Text)  # The actual user message extracted from email

    # Email metadata
    email_date = Column(DateTime)
    email_from = Column(String(255))
    email_subject = Column(String(500))

    # Tracking
    is_read = Column(Boolean, default=False)
    is_replied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_reddit_messages_gmail_id', 'gmail_message_id'),
    )
