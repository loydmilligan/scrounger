# n8n Integration for Scrounger

This directory contains n8n workflow configurations for integrating Reddit email notifications with Scrounger.

## Setup Instructions

### 1. Import the Workflow

1. Open your n8n instance
2. Go to **Workflows** > **Import from File**
3. Select `reddit-email-workflow.json`

### 2. Configure Gmail Credentials

1. In n8n, go to **Credentials** > **Add Credential** > **Gmail OAuth2**
2. Follow the OAuth2 setup to connect your Gmail account
3. Update the credential ID in the workflow nodes

### 3. Update the Webhook URL

The default webhook URL is set to `http://scrounger-backend:8000/api/webhook/reddit-email`.

If running n8n outside Docker network, update to:
- Local: `http://localhost:8849/api/webhook/reddit-email`
- Remote: `http://YOUR_SERVER_IP:8849/api/webhook/reddit-email`

### 4. Create Gmail Label (Optional)

Create a label called "Processed" in Gmail to track which emails have been processed.

## Workflow Overview

```
Gmail Trigger → Filter Reddit Emails → Filter Message Types → Send to Scrounger → Mark as Processed
```

### Nodes:

1. **Gmail Trigger**: Polls for new unread emails from Reddit
2. **Filter Reddit Emails**: Ensures email is from redditmail.com
3. **Filter Message Types**: Filters for relevant messages:
   - Chat requests
   - New messages
   - Comment replies
4. **Send to Scrounger**: POSTs email data to webhook endpoint
5. **Mark as Processed**: Adds label to processed emails

## Supported Email Types

The webhook processes these Reddit email notifications:

| Subject Contains | Message Type |
|-----------------|--------------|
| "chat request" | chat_request |
| "new message" | direct_message |
| "replied" | comment_reply |

## API Endpoint

**POST** `/api/webhook/reddit-email`

Request body:
```json
{
  "from_email": "Reddit <noreply@redditmail.com>",
  "to_email": "your-email@gmail.com",
  "subject": "You have a new chat request",
  "body": "Email body text",
  "date": "2026-03-21T22:15:00Z",
  "message_id": "gmail-message-id"
}
```

Response:
```json
{
  "success": true,
  "message": "Processed chat_request from username",
  "lead_id": 123,
  "reddit_message_id": 456
}
```

## Viewing Messages

Access tracked Reddit messages at:
- **API**: `GET /api/webhook/reddit-messages`
- **Frontend**: Navigate to Leads page and view message history

## Troubleshooting

### Emails not being captured
- Check Gmail OAuth credentials are valid
- Verify emails are marked as unread
- Check n8n execution logs

### Webhook failing
- Verify Scrounger backend is running
- Check network connectivity between n8n and Scrounger
- Review backend logs for errors
