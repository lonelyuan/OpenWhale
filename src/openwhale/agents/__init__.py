"""智能体基座与实现。"""

from .base import AgentRunResult, AgentToolCall, BaseChallengeAgent
from .factory import create_agent
from .openai_agent import OpenAIChallengeAgent
from .prompts import MISSION_PROMPT, SYSTEM_PROMPT

__all__ = [
    "AgentRunResult",
    "AgentToolCall",
    "BaseChallengeAgent",
    "OpenAIChallengeAgent",
    "MISSION_PROMPT",
    "SYSTEM_PROMPT",
    "create_agent",
]