"""
Base Agent Class for Multi-AI Agent System

All agents inherit from this base class and implement the run() method.
Agents run autonomously in background tasks, checking conditions and taking actions.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Each agent runs autonomously in the background, performing specific tasks
    like monitoring meetings, generating context, sending notifications, etc.
    """
    
    def __init__(self, name: str, check_interval_seconds: int = 60):
        """
        Initialize the agent.
        
        Args:
            name: Agent name (e.g., "NotificationAgent", "ContextAgent")
            check_interval_seconds: How often the agent checks for work (default: 60 seconds)
        """
        self.name = name
        self.check_interval = check_interval_seconds
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self._stats = {
            "started_at": None,
            "last_run_at": None,
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "last_error": None
        }
        
    async def start(self):
        """Start the agent's background task."""
        if self.is_running:
            logger.warning(f"Agent {self.name} is already running")
            return
            
        self.is_running = True
        self._stats["started_at"] = datetime.utcnow()
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"✅ Agent {self.name} started (checking every {self.check_interval}s)")
        
    async def stop(self):
        """Stop the agent's background task."""
        if not self.is_running:
            return
            
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"🛑 Agent {self.name} stopped")
        
    async def _run_loop(self):
        """Main loop that runs the agent at the specified interval."""
        logger.info(f"🔄 Agent {self.name} loop started")
        
        while self.is_running:
            try:
                # Execute the agent's main logic
                self._stats["total_runs"] += 1
                self._stats["last_run_at"] = datetime.utcnow()
                
                await self.run()
                
                self._stats["successful_runs"] += 1
                
            except Exception as e:
                self._stats["failed_runs"] += 1
                self._stats["last_error"] = str(e)
                logger.error(f"❌ Agent {self.name} error: {e}", exc_info=True)
            
            # Wait for next interval
            await asyncio.sleep(self.check_interval)
    
    @abstractmethod
    async def run(self):
        """
        Main agent logic - must be implemented by each agent.
        
        This method is called periodically (every check_interval seconds).
        Agents should check for work and perform their specific tasks here.
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status and statistics.
        
        Returns:
            Dictionary containing agent status, stats, and metadata
        """
        return {
            "name": self.name,
            "is_running": self.is_running,
            "check_interval_seconds": self.check_interval,
            "stats": {
                "started_at": self._stats["started_at"].isoformat() if self._stats["started_at"] else None,
                "last_run_at": self._stats["last_run_at"].isoformat() if self._stats["last_run_at"] else None,
                "total_runs": self._stats["total_runs"],
                "successful_runs": self._stats["successful_runs"],
                "failed_runs": self._stats["failed_runs"],
                "success_rate": (
                    round(self._stats["successful_runs"] / self._stats["total_runs"] * 100, 2)
                    if self._stats["total_runs"] > 0 else 0
                ),
                "last_error": self._stats["last_error"]
            }
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' running={self.is_running}>"
