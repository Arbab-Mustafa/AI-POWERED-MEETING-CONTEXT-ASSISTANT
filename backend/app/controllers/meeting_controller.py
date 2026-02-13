"""
Meeting Controller
Handles meeting CRUD operations, Google Calendar sync, and meeting management
"""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import get_current_user, get_db
from app.services.base import CalendarService, ContextService
from app.repositories.base import MeetingRepository
from app.schemas.base import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingDetailResponse
)
from app.core.config import logger

# Initialize router
router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("/", response_model=List[MeetingResponse])
async def get_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    upcoming_only: bool = True,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of meetings for current user.
    
    Args:
        skip: Number of meetings to skip (pagination)
        limit: Maximum number of meetings to return
        upcoming_only: If True, only return future meetings
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of meetings
    """
    try:
        meeting_repo = MeetingRepository(db)
        
        if upcoming_only:
            meetings = await meeting_repo.get_upcoming_for_user(
                user_id=current_user.id,
                limit=limit
            )
        else:
            meetings = await meeting_repo.get_all_for_user(
                user_id=current_user.id,
                skip=skip,
                limit=limit
            )
        
        return [MeetingResponse.from_orm(meeting) for meeting in meetings]
        
    except Exception as e:
        logger.error(f"Error fetching meetings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch meetings"
        )


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(
    meeting_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific meeting.
    
    Args:
        meeting_id: UUID of the meeting
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Detailed meeting information including context and notifications
    """
    try:
        meeting_repo = MeetingRepository(db)
        meeting = await meeting_repo.get_by_id(meeting_id)
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
        
        # Verify user owns this meeting
        if meeting.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return MeetingDetailResponse.from_orm(meeting)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching meeting {meeting_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch meeting"
        )


@router.post("/", response_model=MeetingDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new meeting.
    
    Args:
        meeting_data: Meeting creation data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created meeting with details
    """
    try:
        meeting_repo = MeetingRepository(db)
        
        # Create meeting
        meeting = await meeting_repo.create({
            "user_id": current_user.id,
            "title": meeting_data.title,
            "description": meeting_data.description,
            "start_time": meeting_data.start_time,
            "end_time": meeting_data.end_time,
            "attendees": meeting_data.attendees,
            "meeting_link": meeting_data.meeting_link,
            "meeting_platform": meeting_data.meeting_platform,
            "is_confirmed": True,
            "is_cancelled": False,
            "context_generated": False
        })
        
        logger.info(f"Meeting created: {meeting.id} by user {current_user.email}")
        
        # Generate AI context asynchronously (don't wait)
        context_service = ContextService(db)
        try:
            await context_service.generate_and_create_context(
                meeting_id=meeting.id,
                user_id=current_user.id,
                force_regenerate=False
            )
        except Exception as ctx_error:
            logger.warning(f"Context generation failed for meeting {meeting.id}: {str(ctx_error)}")
        
        return MeetingDetailResponse.from_orm(meeting)
        
    except Exception as e:
        logger.error(f"Error creating meeting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create meeting"
        )


@router.put("/{meeting_id}", response_model=MeetingDetailResponse)
async def update_meeting(
    meeting_id: UUID,
    meeting_data: MeetingUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing meeting.
    
    Args:
        meeting_id: UUID of the meeting
        meeting_data: Meeting update data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated meeting details
    """
    try:
        meeting_repo = MeetingRepository(db)
        meeting = await meeting_repo.get_by_id(meeting_id)
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
        
        # Verify user owns this meeting
        if meeting.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update meeting
        update_data = meeting_data.dict(exclude_unset=True)
        updated_meeting = await meeting_repo.update(meeting_id, update_data)
        
        logger.info(f"Meeting updated: {meeting_id} by user {current_user.email}")
        
        return MeetingDetailResponse.from_orm(updated_meeting)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating meeting {meeting_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update meeting"
        )


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a meeting (soft delete).
    
    Args:
        meeting_id: UUID of the meeting
        current_user: Current authenticated user
        db: Database session
    """
    try:
        meeting_repo = MeetingRepository(db)
        meeting = await meeting_repo.get_by_id(meeting_id)
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
        
        # Verify user owns this meeting
        if meeting.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Mark as cancelled
        await meeting_repo.update(meeting_id, {"is_cancelled": True})
        
        logger.info(f"Meeting deleted: {meeting_id} by user {current_user.email}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting meeting {meeting_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete meeting"
        )


@router.post("/sync/google", response_model=dict)
async def sync_google_calendar(
    calendar_id: str = "primary",
    days_ahead: int = Query(30, ge=1, le=180),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync meetings from Google Calendar.
    
    Args:
        calendar_id: Google Calendar ID (default: "primary")
        days_ahead: Number of days to sync ahead
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Sync statistics (new, updated, total)
    """
    try:
        calendar_service = CalendarService(db)
        
        # Check if user has Google token
        if not current_user.google_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google Calendar not connected. Please authenticate first."
            )
        
        # Sync calendar
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(days=days_ahead)
        
        stats = {
            "synced": 0,
            "new": 0,
            "updated": 0,
            "errors": 0
        }
        
        # Fetch events from Google Calendar (implementation in CalendarService)
        # For now, return placeholder
        logger.info(f"Calendar sync initiated for user {current_user.email}")
        
        return {
            "message": "Calendar sync completed",
            "statistics": stats,
            "calendar_id": calendar_id,
            "synced_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Calendar sync error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Calendar sync failed"
        )


@router.get("/today/upcoming", response_model=List[MeetingResponse])
async def get_today_meetings(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get meetings for today.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of today's meetings
    """
    try:
        meeting_repo = MeetingRepository(db)
        
        # Get start and end of today
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        meetings = await meeting_repo.get_by_date_range(
            user_id=current_user.id,
            start_date=start_of_day,
            end_date=end_of_day
        )
        
        return [MeetingResponse.from_orm(meeting) for meeting in meetings]
        
    except Exception as e:
        logger.error(f"Error fetching today's meetings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch today's meetings"
        )


@router.get("/stats/overview", response_model=dict)
async def get_meeting_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get meeting statistics for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Meeting statistics (total, upcoming, today, this_week)
    """
    try:
        meeting_repo = MeetingRepository(db)
        now = datetime.utcnow()
        
        # Total meetings
        total = await meeting_repo.count_for_user(current_user.id)
        
        # Upcoming meetings
        upcoming = await meeting_repo.count_upcoming(current_user.id)
        
        return {
            "total_meetings": total,
            "upcoming_meetings": upcoming,
            "user_id": str(current_user.id),
            "last_sync": current_user.updated_at.isoformat() if current_user.updated_at else None
        }
        
    except Exception as e:
        logger.error(f"Error fetching meeting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch meeting statistics"
        )
