"""
AI Service for generating meeting context using Ollama/Mistral.
"""

import logging
import httpx
import json
from typing import Dict, List, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIContextGenerator:
    """Generate AI-powered meeting context using Mistral via Ollama."""
    
    def __init__(self):
        self.base_url = settings.MISTRAL_BASE_URL
        self.model_name = "mistral:latest"
        self.timeout = 60.0
    
    async def generate_meeting_context(
        self,
        title: str,
        description: Optional[str],
        attendees: List[str],
        start_time: datetime,
        previous_contexts: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate comprehensive meeting context using AI.
        
        Args:
            title: Meeting title
            description: Meeting description
            attendees: List of attendee emails/names
            start_time: Meeting start time
            previous_contexts: Historical context for learning
        
        Returns:
            Dict with generated context including brief, topics, checklist, etc.
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(
                title, description, attendees, start_time, previous_contexts
            )
            
            # Call Ollama API
            response = await self._call_ollama(prompt)
            
            # Parse and structure the response
            context = self._parse_response(response)
            
            logger.info(f"Generated AI context for meeting: {title}")
            return context
            
        except Exception as e:
            logger.error(f"Error generating AI context: {e}", exc_info=True)
            # Return fallback context
            return self._get_fallback_context(title, description)
    
    def _build_prompt(
        self,
        title: str,
        description: Optional[str],
        attendees: List[str],
        start_time: datetime,
        previous_contexts: Optional[List[Dict]]
    ) -> str:
        """Build the prompt for Mistral."""
        
        attendee_list = ", ".join(attendees) if attendees else "No attendees listed"
        desc_text = description or "No description provided"
        
        prompt = f"""You are an AI assistant that helps professionals prepare for meetings. Analyze this meeting and provide structured context.

Meeting Details:
- Title: {title}
- Description: {desc_text}
- Start Time: {start_time.strftime('%Y-%m-%d %H:%M')}
- Attendees: {attendee_list}

Please provide a comprehensive analysis in the following JSON format:
{{
    "meeting_type": "<type: one_on_one, team_sync, client_call, brainstorm, review, planning, or general>",
    "ai_brief": "<2-3 sentence summary of what this meeting is about and key objectives>",
    "key_topics": ["<topic 1>", "<topic 2>", "<topic 3>"],
    "preparation_checklist": ["<action 1>", "<action 2>", "<action 3>"],
    "suggested_agenda": ["<item 1>", "<item 2>", "<item 3>"],
    "estimated_importance": "<high, medium, or low>",
    "recommended_prep_time": "<minutes>",
    "attendee_roles": {{"<attendee_email>": "<likely role/context>"}},
    "potential_outcomes": ["<outcome 1>", "<outcome 2>"],
    "follow_up_suggestions": ["<suggestion 1>", "<suggestion 2>"]
}}

Respond ONLY with valid JSON, no additional text."""

        # Add learning from previous contexts if available
        if previous_contexts and len(previous_contexts) > 0:
            prompt += f"\n\nPrevious similar meetings:\n"
            for ctx in previous_contexts[:3]:  # Limit to 3 most recent
                prompt += f"- {ctx.get('title', 'N/A')}: {ctx.get('type', 'general')}\n"
        
        return prompt
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate response."""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "")
        
        except httpx.HTTPError as e:
            logger.error(f"Ollama API HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise
    
    def _parse_response(self, response: str) -> Dict:
        """Parse AI response and extract structured data."""
        
        try:
            # Try to extract JSON from response
            # Sometimes Mistral adds extra text, so find JSON block
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                
                # Validate and return structured context
                return {
                    "meeting_type": data.get("meeting_type", "general"),
                    "ai_brief": data.get("ai_brief", data.get("brief", "")),  # Support both keys
                    "key_topics": data.get("key_topics", data.get("topics", [])),
                    "preparation_checklist": data.get("preparation_checklist", data.get("checklist", [])),
                    "suggested_agenda": data.get("suggested_agenda", data.get("agenda", [])),
                    "estimated_importance": data.get("estimated_importance", data.get("importance", "medium")),
                    "recommended_prep_time": data.get("recommended_prep_time", data.get("prep_time", "15")),
                    "attendee_context": data.get("attendee_roles", data.get("attendees", {})),
                    "potential_outcomes": data.get("potential_outcomes", data.get("outcomes", [])),
                    "follow_up_suggestions": data.get("follow_up_suggestions", data.get("follow_up", [])),
                    "confidence_score": 85  # Base confidence score
                }
            else:
                raise ValueError("No valid JSON found in response")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response}")
            raise
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            raise
    
    def _get_fallback_context(self, title: str, description: Optional[str]) -> Dict:
        """Return a basic fallback context when AI generation fails."""
        
        return {
            "meeting_type": "general",
            "ai_brief": f"Meeting: {title}. {description or 'No description provided.'}",
            "key_topics": ["Meeting objectives", "Key discussion points", "Action items"],
            "preparation_checklist": ["Review meeting agenda", "Prepare questions", "Gather relevant materials"],
            "suggested_agenda": ["Introduction and context", "Main discussion topics", "Decision points", "Action items and next steps"],
            "estimated_importance": "medium",
            "recommended_prep_time": "10",
            "attendee_context": {},
            "potential_outcomes": ["Clear action items", "Next steps defined", "Alignment achieved"],
            "follow_up_suggestions": ["Send meeting notes", "Schedule follow-up if needed", "Track action items"],
            "confidence_score": 50  # Low confidence for fallback
        }
    
    async def generate_batch_contexts(
        self,
        meetings: List[Dict]
    ) -> List[Dict]:
        """Generate contexts for multiple meetings efficiently."""
        
        contexts = []
        for meeting in meetings:
            try:
                context = await self.generate_meeting_context(
                    title=meeting.get("title", ""),
                    description=meeting.get("description"),
                    attendees=meeting.get("attendees", []),
                    start_time=meeting.get("start_time", datetime.now()),
                    previous_contexts=meeting.get("previous_contexts")
                )
                contexts.append({
                    "meeting_id": meeting.get("id"),
                    "context": context,
                    "success": True
                })
            except Exception as e:
                logger.error(f"Failed to generate context for meeting {meeting.get('id')}: {e}")
                contexts.append({
                    "meeting_id": meeting.get("id"),
                    "context": self._get_fallback_context(
                        meeting.get("title", "Unknown"),
                        meeting.get("description")
                    ),
                    "success": False,
                    "error": str(e)
                })
        
        return contexts
    
    async def enhance_context_with_learning(
        self,
        base_context: Dict,
        user_feedback: Optional[Dict] = None,
        meeting_outcome: Optional[Dict] = None
    ) -> Dict:
        """Enhance context using user feedback and meeting outcomes."""
        
        enhanced = base_context.copy()
        
        if user_feedback:
            # Adjust confidence based on feedback
            if user_feedback.get("helpful", False):
                enhanced["confidence"] = min(95, enhanced.get("confidence", 85) + 10)
            else:
                enhanced["confidence"] = max(60, enhanced.get("confidence", 85) - 10)
        
        if meeting_outcome:
            # Store for future learning
            enhanced["actual_outcome"] = meeting_outcome.get("summary", "")
            enhanced["effectiveness_rating"] = meeting_outcome.get("rating", 3)
        
        return enhanced


# Singleton instance
ai_generator = AIContextGenerator()
