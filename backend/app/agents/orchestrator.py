"""
Agent Orchestrator - Manages all AI agents in the system

The orchestrator coordinates multiple autonomous agents, starting/stopping them,
monitoring their health, and providing a unified interface for agent management.
"""

from typing import List, Dict, Any
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Manages all AI agents in the ContextMeet system.
    
    The orchestrator:
    - Starts and stops all agents
    - Monitors agent health and status
    - Provides unified interface for agent management
    - Handles agent lifecycle
    """
    
    def __init__(self):
        """Initialize the orchestrator with an empty agent registry."""
        self.agents: List[BaseAgent] = []
        self.is_running = False
        
    def register_agent(self, agent: BaseAgent):
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent instance to register
        """
        if agent in self.agents:
            logger.warning(f"Agent {agent.name} is already registered")
            return
            
        self.agents.append(agent)
        logger.info(f"📝 Registered agent: {agent.name}")
        
    async def start_all(self):
        """Start all registered agents."""
        if self.is_running:
            logger.warning("Orchestrator is already running")
            return
            
        logger.info(f"🚀 Starting agent orchestrator with {len(self.agents)} agents...")
        
        for agent in self.agents:
            try:
                await agent.start()
            except Exception as e:
                logger.error(f"Failed to start agent {agent.name}: {e}", exc_info=True)
        
        self.is_running = True
        logger.info("✅ Agent orchestrator started successfully")
        
    async def stop_all(self):
        """Stop all registered agents."""
        if not self.is_running:
            return
            
        logger.info("🛑 Stopping agent orchestrator...")
        
        for agent in self.agents:
            try:
                await agent.stop()
            except Exception as e:
                logger.error(f"Failed to stop agent {agent.name}: {e}", exc_info=True)
        
        self.is_running = False
        logger.info("✅ Agent orchestrator stopped")
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all agents.
        
        Returns:
            Dictionary containing orchestrator status and all agent statuses
        """
        agent_statuses = [agent.get_status() for agent in self.agents]
        
        running_count = sum(1 for agent in self.agents if agent.is_running)
        
        return {
            "orchestrator_running": self.is_running,
            "total_agents": len(self.agents),
            "running_agents": running_count,
            "stopped_agents": len(self.agents) - running_count,
            "agents": agent_statuses
        }
    
    def get_agent(self, name: str) -> BaseAgent:
        """
        Get an agent by name.
        
        Args:
            name: Agent name to search for
            
        Returns:
            Agent instance or None if not found
        """
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None


# Global orchestrator instance
orchestrator = AgentOrchestrator()


async def start_agent_system():
    """Start the multi-agent system (called from FastAPI startup)."""
    await orchestrator.start_all()


async def shutdown_agent_system():
    """Shutdown the multi-agent system (called from FastAPI shutdown)."""
    await orchestrator.stop_all()
