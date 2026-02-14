"""
Background task scheduler for automatic notification delivery.
Uses APScheduler to check database every minute for notifications to send.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta

from app.core.config import db_manager
from app.services.base import NotificationService

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def send_pending_notifications():
    """
    Check database for notifications scheduled to be sent now.
    Runs every minute via APScheduler.
    """
    try:
        logger.info("Checking for pending notifications...")
        
        async with db_manager.AsyncSessionLocal() as db:
            notification_service = NotificationService(db)
            
            # Get notifications that should be sent (scheduled_time <= now)
            pending = await notification_service.get_pending_notifications()
            
            if not pending or len(pending) == 0:
                logger.debug("No pending notifications to send")
                return
            
            logger.info(f"Found {len(pending)} pending notifications to send")
            
            # Send each notification
            sent_count = 0
            failed_count = 0
            
            for notification in pending:
                try:
                    # Send via notification service
                    success = await notification_service.send_notification(notification.id)
                    
                    if success:
                        sent_count += 1
                        logger.info(f"✅ Sent notification {notification.id} for meeting {notification.meeting_id}")
                    else:
                        failed_count += 1
                        logger.error(f"❌ Failed to send notification {notification.id}")
                        
                except Exception as send_error:
                    failed_count += 1
                    logger.error(f"Error sending notification {notification.id}: {send_error}", exc_info=True)
            
            logger.info(f"Notification batch complete: {sent_count} sent, {failed_count} failed")
            
    except Exception as e:
        logger.error(f"Error in send_pending_notifications: {e}", exc_info=True)


async def start_notification_scheduler():
    """Start the background notification scheduler."""
    try:
        # Add job to run every minute
        scheduler.add_job(
            send_pending_notifications,
            IntervalTrigger(minutes=1),
            id='send_notifications',
            name='Send Pending Notifications',
            replace_existing=True,
            max_instances=1  # Prevent overlapping runs
        )
        
        # Start scheduler
        scheduler.start()
        
        logger.info("✅ Notification scheduler started - checking every minute")
        logger.info(f"Next run: {scheduler.get_job('send_notifications').next_run_time}")
        
    except Exception as e:
        logger.error(f"Failed to start notification scheduler: {e}", exc_info=True)
        raise


async def shutdown_scheduler():
    """Shutdown the notification scheduler gracefully."""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=True)
            logger.info("Notification scheduler shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down scheduler: {e}")


# Export functions
__all__ = ['start_notification_scheduler', 'shutdown_scheduler']
