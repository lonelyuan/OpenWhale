"""智能体工厂。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .openai_agent import OpenAIChallengeAgent


def create_agent(config: dict[str, str], on_message: Callable[[str, str], None] | None = None):
    """根据配置创建智能体实例。"""
    backend = config.get("AGENT_BACKEND", "openai_compat").lower()

    if backend in {"openai", "openai_compat", "minimax", "chat_completions"}:
        return OpenAIChallengeAgent(
            api_key=config["MODEL_API_KEY"],
            base_url=config["MODEL_BASE_URL"],
            model=config["MODEL_ID"],
            model_name=config["MODEL_NAME"],
            on_message=on_message,
        )

    raise NotImplementedError(
        f"暂不支持的智能体基座: {backend}. 目前可用: openai_compat/minimax/openai/chat_completions"
    )