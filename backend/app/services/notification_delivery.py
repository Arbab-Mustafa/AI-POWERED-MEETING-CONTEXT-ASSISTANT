"""
Notification Delivery Service for Email and Telegram.
"""

import logging
import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime

from app.core.config import settings
from app.models.db import Notification, Meeting, Context

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Service for sending email notifications via Gmail SMTP."""
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = settings.GMAIL_EMAIL
        self.sender_password = settings.GMAIL_APP_PASSWORD
    
    async def send_meeting_reminder(
        self,
        to_email: str,
        meeting: Meeting,
        context: Optional[Context] = None,
        minutes_until: int = 30,
        to_all_attendees: bool = False
    ) -> bool:
        """
        Send meeting reminder email.
        
        Args:
            to_email: Recipient email
            meeting: Meeting object
            context: AI-generated context (optional)
            minutes_until: Minutes until meeting starts
        
        Returns:
            True if sent successfully, False otherwise
        """
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"ContextMeet <{self.sender_email}>"
            msg['To'] = to_email
            
            # Different subject line for meeting creation vs reminders
            if minutes_until == 0:
                msg['Subject'] = f"Meeting Created: {meeting.title}"
            else:
                msg['Subject'] = f"Reminder: {meeting.title} in {minutes_until} minutes"
            
            # Create HTML content
            html_content = self._build_reminder_html(meeting, context, minutes_until)
            
            # Create plain text content
            text_content = self._build_reminder_text(meeting, context, minutes_until)
            
            # Attach both parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Sent email reminder for meeting {meeting.id} to {to_email}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email reminder: {e}")
            return False
    
    def _build_reminder_html(
        self,
        meeting: Meeting,
        context: Optional[Context],
        minutes_until: int
    ) -> str:
        """Build HTML email content."""
        
        start_time_str = meeting.start_time.strftime('%I:%M %p') if meeting.start_time else 'Unknown'
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
        .content {{ background: #f9f9f9; padding: 20px; margin-top: 20px; border-radius: 8px; }}
        .meeting-info {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea; }}
        .context-box {{ background: #e8f4f8; padding: 15px; margin: 15px 0; border-radius: 6px; }}
        .btn {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 15px; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        ul {{ padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 Meeting Reminder</h1>
            <p><strong>{meeting.title}</strong> starts in <strong>{minutes_until} minutes</strong></p>
        </div>
        
        <div class="content">
            <div class="meeting-info">
                <h3>📅 Meeting Details</h3>
                <p><strong>Time:</strong> {start_time_str}</p>
                <p><strong>Duration:</strong> {self._calculate_duration(meeting)} minutes</p>
                {f'<p><strong>Description:</strong> {meeting.description}</p>' if meeting.description else ''}
                {f'<p><strong>Attendees:</strong> {", ".join([a if isinstance(a, str) else (a.get("email") or a.get("name", "Unknown")) for a in meeting.attendees[:5]])}</p>' if meeting.attendees else ''}
            </div>
"""
        
        # Add AI context if available
        if context and context.ai_brief:
            html += f"""
            <div class="context-box">
                <h3>🤖 AI-Generated Context</h3>
                <p><strong>Meeting Type:</strong> {context.meeting_type.replace('_', ' ').title()}</p>
                <p>{context.ai_brief}</p>
                
                {f'''
                <h4>Key Topics:</h4>
                <ul>
                    {"".join(f"<li>{topic}</li>" for topic in context.key_topics[:5])}
                </ul>
                ''' if context.key_topics else ''}
                
                {f'''
                <h4>Preparation Checklist:</h4>
                <ul>
                    {"".join(f"<li>{item}</li>" for item in context.preparation_checklist[:5])}
                </ul>
                ''' if context.preparation_checklist else ''}
            </div>
"""
        
        # Add join button if meeting link exists
        if meeting.meeting_link:
            html += f"""
            <div style="text-align: center;">
                <a href="{meeting.meeting_link}" class="btn">🎥 Join Meeting</a>
            </div>
"""
        
        html += f"""
        </div>
        
        <div class="footer">
            <p>Sent by ContextMeet - Your AI Meeting Assistant</p>
            <p>Powered by Mistral AI</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _build_reminder_text(
        self,
        meeting: Meeting,
        context: Optional[Context],
        minutes_until: int
    ) -> str:
        """Build plain text email content."""
        
        start_time_str = meeting.start_time.strftime('%I:%M %p') if meeting.start_time else 'Unknown'
        
        text = f"""
MEETING REMINDER
{'=' * 50}

{meeting.title} starts in {minutes_until} minutes

DETAILS:
Time: {start_time_str}
Duration: {self._calculate_duration(meeting)} minutes
"""
        
        if meeting.description:
            text += f"Description: {meeting.description}\n"
        
        if meeting.attendees:
            attendee_names = [a if isinstance(a, str) else (a.get('email') or a.get('name', 'Unknown')) for a in meeting.attendees[:5]]
            text += f"Attendees: {', '.join(attendee_names)}\n"
        
        if context and context.ai_brief:
            text += f"\nAI-GENERATED CONTEXT:\n{context.ai_brief}\n"
            
            if context.key_topics:
                text += f"\nKey Topics:\n"
                for topic in context.key_topics[:5]:
                    text += f"  • {topic}\n"
            
            if context.preparation_checklist:
                text += f"\nPreparation Checklist:\n"
                for item in context.preparation_checklist[:5]:
                    text += f"  • {item}\n"
        
        if meeting.meeting_link:
            text += f"\nJoin Meeting: {meeting.meeting_link}\n"
        
        text += "\n" + "=" * 50
        text += "\nSent by ContextMeet - Your AI Meeting Assistant"
        
        return text
    
    def _calculate_duration(self, meeting: Meeting) -> int:
        """Calculate meeting duration in minutes."""
        if meeting.start_time and meeting.end_time:
            delta = meeting.end_time - meeting.start_time
            return int(delta.total_seconds() / 60)
        return 30  # Default


class TelegramNotificationService:
    """Service for sending notifications via Telegram Bot."""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_meeting_reminder(
        self,
        chat_id: str,
        meeting: Meeting,
        context: Optional[Context] = None,
        minutes_until: int = 15
    ) -> bool:
        """
        Send meeting reminder via Telegram.
        
        Args:
            chat_id: Telegram chat ID
            meeting: Meeting object
            context: AI-generated context (optional)
            minutes_until: Minutes until meeting starts
        
        Returns:
            True if sent successfully, False otherwise
        """
        
        try:
            # Build message
            message = self._build_telegram_message(meeting, context, minutes_until)
            
            # Prepare inline keyboard if meeting link exists
            reply_markup = None
            if meeting.meeting_link:
                reply_markup = {
                    "inline_keyboard": [[
                        {
                            "text": "🎥 Join Meeting",
                            "url": meeting.meeting_link
                        }
                    ]]
                }
            
            # Send message
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }
            
            if reply_markup:
                payload["reply_markup"] = reply_markup
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
            
            logger.info(f"Sent Telegram reminder for meeting {meeting.id} to chat {chat_id}")
            return True
            
        except httpx.HTTPError as e:
            logger.error(f"Telegram API HTTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send Telegram reminder: {e}")
            return False
    
    def _build_telegram_message(
        self,
        meeting: Meeting,
        context: Optional[Context],
        minutes_until: int
    ) -> str:
        """Build Telegram message content with Markdown."""
        
        start_time_str = meeting.start_time.strftime('%I:%M %p') if meeting.start_time else 'Unknown'
        
        message = f"""
🔔 *Meeting Reminder*

*{meeting.title}* starts in *{minutes_until} minutes*

📅 *Details:*
• Time: {start_time_str}
• Duration: {self._calculate_duration(meeting)} minutes
"""
        
        if meeting.description:
            # Escape special characters for Markdown
            desc = meeting.description.replace('_', '\\_').replace('*', '\\*')
            message += f"• Description: {desc}\n"
        
        if meeting.attendees:
            attendee_names = [a if isinstance(a, str) else (a.get('email') or a.get('name', 'Unknown')) for a in meeting.attendees[:3]]
            attendee_list = ', '.join(attendee_names)
            if len(meeting.attendees) > 3:
                attendee_list += f" +{len(meeting.attendees) - 3} more"
            message += f"• Attendees: {attendee_list}\n"
        
        # Add AI context if available
        if context and context.ai_brief:
            message += f"\n🤖 *AI Context:*\n{context.ai_brief}\n"
            
            if context.key_topics:
                message += f"\n📌 *Key Topics:*\n"
                for topic in context.key_topics[:3]:
                    message += f"  • {topic}\n"
            
            if context.preparation_checklist:
                message += f"\n✅ *Quick Prep:*\n"
                for item in context.preparation_checklist[:3]:
                    message += f"  • {item}\n"
        
        return message
    
    def _calculate_duration(self, meeting: Meeting) -> int:
        """Calculate meeting duration in minutes."""
        if meeting.start_time and meeting.end_time:
            delta = meeting.end_time - meeting.start_time
            return int(delta.total_seconds() / 60)
        return 30  # Default


class NotificationDispatcher:
    """Main dispatcher for all notification channels."""
    
    def __init__(self):
        self.email_service = EmailNotificationService()
        self.telegram_service = TelegramNotificationService()
    
    async def send_notification(
        self,
        notification: Notification,
        meeting: Meeting,
        user_email: str,
        telegram_chat_id: Optional[str] = None,
        context: Optional[Context] = None
    ) -> bool:
        """
        Send notification through the appropriate channel.
        
        Args:
            notification: Notification object
            meeting: Meeting object
            user_email: User's email address
            telegram_chat_id: Telegram chat ID (if applicable)
            context: AI context (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        
        # Calculate minutes until meeting
        if meeting.start_time:
            time_diff = meeting.start_time - datetime.utcnow()
            minutes_until = int(time_diff.total_seconds() / 60)
        else:
            minutes_until = 0
        
        try:
            if notification.channel == "email":
                return await self.email_service.send_meeting_reminder(
                    to_email=user_email,
                    meeting=meeting,
                    context=context,
                    minutes_until=minutes_until
                )
            
            elif notification.channel == "telegram":
                if not telegram_chat_id:
                    logger.warning(f"No Telegram chat ID for user, skipping notification {notification.id}")
                    return False
                
                return await self.telegram_service.send_meeting_reminder(
                    chat_id=telegram_chat_id,
                    meeting=meeting,
                    context=context,
                    minutes_until=minutes_until
                )
            
            elif notification.channel == "sms":
                # SMS not implemented yet
                logger.warning(f"SMS notifications not implemented, skipping {notification.id}")
                return False
            
            else:
                logger.error(f"Unknown notification channel: {notification.channel}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {e}")
            return False


# Singleton instance
notification_dispatcher = NotificationDispatcher()
