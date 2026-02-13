"""
Notification Controller
Handles notification scheduling, delivery, and tracking
"""
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import get_current_user, get_db
from app.services.base import NotificationService
from app.repositories.base import NotificationRepository, MeetingRepository
from app.schemas.base import NotificationCreate, NotificationResponse
from app.core.config import logger

# Initialize router
router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    status_filter: str = Query(None, regex="^(pending|sent|delivered|failed)$"),
    current_user = Depends(get_current_user),
    db: AsyncSession =Depends(get_db)
):
    """
    Get notifications for current user.
    
    Args:
        skip: Number of notifications to skip
        limit: Maximum number to return
        status_filter: Filter by status
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of notifications
    """
    try:
        notification_repo = NotificationRepository(db)
        
        notifications = await notification_repo.get_for_user(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status=status_filter
        )
        
        return [NotificationResponse.from_orm(notif) for notif in notifications]
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )


@router.post("/schedule", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def schedule_notification(
    notification_data: NotificationCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Schedule a notification for a meeting.
    
    Args:
        notification_data: Notification schedule data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created notification
    """
    try:
        notification_service = NotificationService(db)
        meeting_repo = MeetingRepository(db)
        
        # Verify meeting exists and belongs to user
        meeting = await meeting_repo.get_by_id(notification_data.meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
        
        if meeting.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Schedule notification
        notification = await notification_service.schedule_notification(
            meeting_id=notification_data.meeting_id,
            user_id=current_user.id,
            channel=notification_data.channel,
            scheduled_time=notification_data.scheduled_time
        )
        
        logger.info(f"Notification scheduled: {notification.id} for meeting {notification_data.meeting_id}")
        
        return NotificationResponse.from_orm(notification)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule notification"
        )


@router.post("/meeting/{meeting_id}/auto-schedule", response_model=List[NotificationResponse])
async def auto_schedule_notifications(
    meeting_id: UUID,
    channels: List[str] = Query(default=["email"], description="Notification channels"),
    reminder_minutes: List[int] = Query([60, 15], description="Minutes before meeting"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Auto-schedule notifications for a meeting based on user preferences.
    
    Args:
        meeting_id: UUID of the meeting
        channels: Notification channels (email, telegram, sms)
        reminder_minutes: Minutes before meeting to send reminders
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of scheduled notifications
    """
    try:
        notification_service = NotificationService(db)
        meeting_repo = MeetingRepository(db)
        
        # Verify meeting
        meeting = await meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
        
        if meeting.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Schedule notifications
        notifications = await notification_service.schedule_notifications(
            meeting=meeting,
            channels=channels,
            reminder_minutes_list=reminder_minutes
        )
        
        logger.info(f"Auto-scheduled {len(notifications)} notifications for meeting {meeting_id}")
        
        return [NotificationResponse.from_orm(notif) for notif in notifications]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error auto-scheduling notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to auto-schedule notifications"
        )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_notification(
    notification_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a scheduled notification.
    
    Args:
        notification_id: UUID of the notification
        current_user: Current authenticated user
        db: Database session
    """
    try:
        notification_repo = NotificationRepository(db)
        notification = await notification_repo.get_by_id(notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Verify user owns this notification
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Only allow canceling pending notifications
        if notification.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel {notification.status} notification"
            )
        
        # Update status to cancelled
        await notification_repo.update(notification_id, {"status": "cancelled"})
        
        logger.info(f"Notification cancelled: {notification_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling notification {notification_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel notification"
        )


@router.get("/pending/upcoming", response_model=List[NotificationResponse])
async def get_pending_notifications(
    hours_ahead: int = Query(24, ge=1, le=168),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending notifications scheduled in the next N hours.
    
    Args:
        hours_ahead: Number of hours to look ahead
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of pending notifications
    """
    try:
        notification_repo = NotificationRepository(db)
        
        # Get notifications within time window
        end_time = datetime.utcnow() + timedelta(hours=hours_ahead)
        
        notifications = await notification_repo.get_pending(
            user_id=current_user.id,
            before_time=end_time
        )
        
        return [NotificationResponse.from_orm(notif) for notif in notifications]
        
    except Exception as e:
        logger.error(f"Error fetching pending notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending notifications"
        )


@router.post("/{notification_id}/resend", response_model=NotificationResponse)
async def resend_notification(
    notification_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resend a failed notification.
    
    Args:
        notification_id: UUID of the notification
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated notification
    """
    try:
        notification_service = NotificationService(db)
        notification_repo = NotificationRepository(db)
        
        notification = await notification_repo.get_by_id(notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Verify user owns this notification
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Only allow resending failed notifications
        if notification.status not in ["failed", "error"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot resend {notification.status} notification"
            )
        
        # Attempt to send again
        success = await notification_service.send_notification(notification)
        
        if success:
            await notification_service.mark_sent(notification.id)
            updated_notification = await notification_repo.get_by_id(notification_id)
            logger.info(f"Notification resent successfully: {notification_id}")
            return NotificationResponse.from_orm(updated_notification)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Resend failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending notification {notification_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend notification"
        )


@router.get("/stats/overview", response_model=dict)
async def get_notification_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get notification statistics for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Notification statistics
    """
    try:
        notification_repo = NotificationRepository(db)
        
        stats = {
            "total": 0,
            "pending": 0,
            "sent": 0,
            "delivered": 0,
            "failed": 0
        }
        
        # Count notifications by status
        for status_type in ["pending", "sent", "delivered", "failed"]:
            count = await notification_repo.count_by_status(
                user_id=current_user.id,
                status=status_type
            )
            stats[status_type] = count
            stats["total"] += count
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching notification stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification statistics"
        )
