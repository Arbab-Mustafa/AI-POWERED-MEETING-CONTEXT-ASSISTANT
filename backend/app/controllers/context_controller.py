"""
Context Controller
Handles AI-generated meeting context, briefs, and preparation insights
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import get_current_user, get_db
from app.services.base import ContextService
from app.repositories.base import ContextRepository, MeetingRepository
from app.schemas.base import ContextCreate, ContextResponse, ContextUpdate
from app.core.config import logger

# Initialize router
router = APIRouter(prefix="/contexts", tags=["contexts"])


@router.get("/meeting/{meeting_id}", response_model=Optional[ContextResponse])
async def get_meeting_context(
    meeting_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated context for a specific meeting.
    
    Args:
        meeting_id: UUID of the meeting
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Meeting context with AI brief and insights, or None if not generated yet
    """
    try:
        context_repo = ContextRepository(db)
        meeting_repo = MeetingRepository(db)
        
        # Verify meeting exists and belongs to user
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
        
        # Get context - return None if not generated yet (not an error)
        context = await context_repo.get_by_meeting_id(meeting_id)
        
        if not context:
            return None
        
        return ContextResponse.model_validate(context)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching context for meeting {meeting_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch meeting context"
        )


@router.post("/generate/{meeting_id}", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
async def generate_context(
    meeting_id: UUID,
    force_regenerate: bool = Query(False, description="Force regenerate even if context exists"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI context for a meeting.
    
    Args:
        meeting_id: UUID of the meeting
        force_regenerate: If True, regenerate even if context exists
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Generated meeting context
    """
    try:
        context_service = ContextService(db)
        context_repo = ContextRepository(db)
        meeting_repo = MeetingRepository(db)
        
        # Verify meeting exists and belongs to user
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
        
        # Check if context already exists
        existing_context = await context_repo.get_by_meeting_id(meeting_id)
        
        if existing_context and not force_regenerate:
            return ContextResponse.model_validate(existing_context)
        
        # Generate AI context using Mistral
        logger.info(f"Generating AI context for meeting {meeting_id}")
        
        try:
            context = await context_service.generate_and_create_context(
                meeting_id=meeting_id,
                user_id=current_user.id,
                force_regenerate=force_regenerate
            )
            
            if not context:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service (Ollama) is not available. Please ensure Ollama is running with: ollama serve"
                )
            
            logger.info(f"Context generated for meeting {meeting_id} with confidence {context.confidence_score}")
            return ContextResponse.model_validate(context)
            
        except Exception as ai_error:
            # Check if it's an Ollama connection error
            error_msg = str(ai_error).lower()
            logger.error(f"AI error during context generation: {ai_error}", exc_info=True)
            if "connection" in error_msg or "refused" in error_msg or "11434" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service (Ollama) is not running. Please start Ollama with 'ollama serve' and ensure the Mistral model is available."
                )
            raise
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating context for meeting {meeting_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate context: {str(e)}"
        )


@router.put("/{context_id}", response_model=ContextResponse)
async def update_context(
    context_id: UUID,
    context_data: ContextUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update meeting context (user edits).
    
    Args:
        context_id: UUID of the context
        context_data: Context update data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated context
    """
    try:
        context_repo = ContextRepository(db)
        context = await context_repo.get_by_id(context_id)
        
        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Context not found"
            )
        
        # Verify user owns this context
        if context.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update context
        update_data = context_data.model_dump(exclude_unset=True)
        update_data["user_edited"] = True
        
        updated_context = await context_repo.update(context_id, update_data)
        
        logger.info(f"Context updated: {context_id} by user {current_user.email}")
        
        return ContextResponse.model_validate(updated_context)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating context {context_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update context"
        )


@router.delete("/{context_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_context(
    context_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete meeting context.
    
    Args:
        context_id: UUID of the context
        current_user: Current authenticated user
        db: Database session
    """
    try:
        context_repo = ContextRepository(db)
        context = await context_repo.get_by_id(context_id)
        
        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Context not found"
            )
        
        # Verify user owns this context
        if context.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete context
        await context_repo.delete(context_id)
        
        logger.info(f"Context deleted: {context_id} by user {current_user.email}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting context {context_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete context"
        )


@router.get("/user/recent", response_model=List[ContextResponse])
async def get_recent_contexts(
    limit: int = Query(10, le=50, ge=1),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent contexts for current user.
    
    Args:
        limit: Maximum number of contexts to return
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of recent contexts
    """
    try:
        context_repo = ContextRepository(db)
        contexts = await context_repo.get_recent_for_user(
            user_id=current_user.id,
            limit=limit
        )
        
        return [ContextResponse.model_validate(context) for context in contexts]
        
    except Exception as e:
        logger.error(f"Error fetching recent contexts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contexts"
        )


@router.post("/batch/generate", response_model=dict)
async def generate_batch_contexts(
    meeting_ids: List[UUID],
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate contexts for multiple meetings (background task).
    
    Args:
        meeting_ids: List of meeting UUIDs
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Task status
    """
    try:
        meeting_repo = MeetingRepository(db)
        
        # Verify all meetings exist and belong to user
        valid_meetings = []
        for meeting_id in meeting_ids:
            meeting = await meeting_repo.get_by_id(meeting_id)
            if meeting and meeting.user_id == current_user.id:
                valid_meetings.append(meeting_id)
        
        if not valid_meetings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid meetings found"
            )
        
        # Add background task for batch generation
        # (In production, use Celery or similar for this)
        logger.info(f"Batch context generation queued for {len(valid_meetings)} meetings")
        
        return {
            "message": "Context generation queued",
            "meetings_queued": len(valid_meetings),
            "meeting_ids": [str(mid) for mid in valid_meetings]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queueing batch context generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue context generation"
        )
