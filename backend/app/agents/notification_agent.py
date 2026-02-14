"""
Notification Agent - Autonomous notification sender

This agent continuously monitors the database for pending notifications
and sends them when their scheduled time arrives.
"""

from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base_agent import BaseAgent
from app.core.config import db_manager
from app.services.base import NotificationService

logger = logging.getLogger(__name__)


class NotificationAgent(BaseAgent):
    """
    Agent that autonomously sends pending notifications.
    
    This agent:
    - Checks database every minute for notifications with scheduled_time <= now
    - Sends notifications via email/telegram
    - Updates notification status in database
    - Retries failed notifications
    """
    
    def __init__(self):
        """Initialize the notification agent (checks every 60 seconds)."""
        super().__init__(name="NotificationAgent", check_interval_seconds=60)
        self.notifications_sent = 0
        
    async def run(self):
        """Check for and send pending notifications."""
        async with db_manager.AsyncSessionLocal() as db:
            notification_service = NotificationService(db)
            
            try:
                # Get pending notifications
                pending = await notification_service.get_pending_notifications()
                
                if not pending:
                    logger.debug(f"[{self.name}] No pending notifications")
                    return
                
                logger.info(f"[{self.name}] Found {len(pending)} pending notifications")
                
                # Send each notification
                sent_count = 0
                for notification in pending:
                    try:
                        success = await notification_service.send_notification(notification.id)
                        if success:
                            sent_count += 1
                            self.notifications_sent += 1
                            logger.info(f"[{self.name}] Sent notification {notification.id}")
                        else:
                            logger.warning(f"[{self.name}] Failed to send notification {notification.id}")
                    except Exception as e:
                        logger.error(f"[{self.name}] Error sending notification {notification.id}: {e}")
                
                if sent_count > 0:
                    logger.info(f"[{self.name}] Successfully sent {sent_count}/{len(pending)} notifications")
                    
            except Exception as e:
                logger.error(f"[{self.name}] Error checking notifications: {e}", exc_info=True)
                
    def get_status(self):
        """Get agent status with notification-specific stats."""
        status = super().get_status()
        status["stats"]["notifications_sent"] = self.notifications_sent
        return status
