"""
Context Agent - Autonomous AI context generator

This agent monitors meetings and automatically generates AI-powered context
for meetings that don't have it yet.
"""

from datetime import datetime, timedelta
import logging
from sqlalchemy import select
from app.agents.base_agent import BaseAgent
from app.models.db import Meeting, Context
from app.services.ai_service import AIContextGenerator
from app.core.config import db_manager

logger = logging.getLogger(__name__)


class ContextAgent(BaseAgent):
    """
    Agent that autonomously generates AI context for meetings.
    
    This agent:
    - Monitors meetings without context
    - Automatically generates AI context using Mistral
    - Prioritizes upcoming meetings
    - Updates meeting with context_generated flag
    """
    
    def __init__(self):
        """Initialize the context agent (checks every 5 minutes)."""
        super().__init__(name="ContextAgent", check_interval_seconds=300)  # 5 minutes
        self.contexts_generated = 0
        
    async def run(self):
        """Check for meetings without context and generate it."""
        async with db_manager.AsyncSessionLocal() as db:
            try:
                # Find meetings without context that are upcoming (within next 7 days)
                seven_days_from_now = datetime.utcnow() + timedelta(days=7)
                
                stmt = select(Meeting).where(
                    Meeting.context_generated == False,
                    Meeting.start_time > datetime.utcnow(),
                    Meeting.start_time <= seven_days_from_now,
                    Meeting.is_cancelled == False
                ).order_by(Meeting.start_time)
                
                result = await db.execute(stmt)
                meetings_without_context = result.scalars().all()
                
                if not meetings_without_context:
                    logger.debug(f"[{self.name}] No meetings need context generation")
                    return
                
                logger.info(f"[{self.name}] Found {len(meetings_without_context)} meetings without context")
                
                # Generate context for each meeting (limit to 5 per run to avoid overload)
                ai_service = AIContextGenerator()
                generated_count = 0
                
                for meeting in meetings_without_context[:5]:
                    try:
                        logger.info(f"[{self.name}] Generating context for meeting {meeting.id}: {meeting.title}")
                        
                        # Generate AI context
                        context_data = await ai_service.generate_meeting_context(
                            title=meeting.title,
                            description=meeting.description or "",
                            attendees=[a.get('email') for a in (meeting.attendees or [])] if isinstance(meeting.attendees, list) else [],
                            start_time=meeting.start_time
                        )
                        
                        # Check if context already exists
                        existing_context = await db.execute(
                            select(Context).where(Context.meeting_id == meeting.id)
                        )
                        if existing_context.scalar_one_or_none():
                            logger.info(f"[{self.name}] Context already exists for meeting {meeting.id}")
                            meeting.context_generated = True
                            await db.commit()
                            continue
                        
                        # Create context record
                        context = Context(
                            meeting_id=meeting.id,
                            user_id=meeting.user_id,  # CRITICAL: Must set user_id
                            ai_brief=context_data["ai_brief"],
                            meeting_type=context_data["meeting_type"],
                            key_topics=context_data["key_topics"],
                            preparation_checklist=context_data["preparation_checklist"],
                            attendee_context=context_data.get("attendee_context", {}),
                            confidence_score=context_data.get("confidence_score", 85),
                            ai_model_version="mistral-7b",
                            user_edited=False
                        )
                        
                        db.add(context)
                        
                        # Update meeting
                        meeting.context_generated = True
                        
                        await db.commit()
                        
                        generated_count += 1
                        self.contexts_generated += 1
                        
                        logger.info(f"[{self.name}] ✅ Generated context for meeting {meeting.id}")
                        
                    except Exception as e:
                        logger.error(f"[{self.name}] Error generating context for meeting {meeting.id}: {e}")
                        await db.rollback()
                
                if generated_count > 0:
                    logger.info(f"[{self.name}] Successfully generated {generated_count} contexts")
                    
            except Exception as e:
                logger.error(f"[{self.name}] Error in context generation: {e}", exc_info=True)
                
    def get_status(self):
        """Get agent status with context-specific stats."""
        status = super().get_status()
        status["stats"]["contexts_generated"] = self.contexts_generated
        return status
