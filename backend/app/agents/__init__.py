"""
Multi-AI Agent System

This package contains autonomous AI agents that run in the background,
performing tasks like generating context, sending notifications, and
monitoring calendar changes.
"""

from .base_agent import BaseAgent
from .orchestrator import orchestrator, start_agent_system, shutdown_agent_system
from .notification_agent import NotificationAgent
from .context_agent import ContextAgent
from .monitor_agent import MonitorAgent

__all__ = [
    "BaseAgent",
    "orchestrator",
    "start_agent_system",
    "shutdown_agent_system",
    "NotificationAgent",
    "ContextAgent",
    "MonitorAgent",
]
