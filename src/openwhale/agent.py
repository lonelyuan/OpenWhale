"""Claude 智能体 - 基于 Anthropic SDK 构建的渗透测试智能体"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

import anthropic
from loguru import logger
from mcp import ClientSession

from .mcp_client import call_tool, list_tools, tools_to_anthropic_format

# 系统提示词 - 渗透测试角色
SYSTEM_PROMPT = """你是 OpenWhale，一个专业的渗透测试 AI 智能体，参与腾讯云黑客松智能渗透挑战赛。

你的任务流程：
1. **侦察（Recon）**：查询所有可用赛题，了解目标信息
2. **检测（Detection）**：分析赛题，识别可能的漏洞类型
3. **利用（Exploitation）**：利用漏洞获取 Flag 并提交

你可以使用提供的 MCP 工具与比赛平台交互。始终保持条理清晰，逐步说明你的行动和发现。
"""

# 侦察技能提示词注入
RECON_SKILL = """
[技能：侦察模式]
当前任务：查询所有可用赛题并分析目标。
- 使用工具查询赛题列表
- 记录每道题的名称、描述、难度和类型
- 输出结构化的侦察报告
"""


class PenetrationAgent:
    """渗透测试智能体 - 主从模式中的主智能体"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4-5",
        max_iterations: int = 10,
        on_message: Callable[[str, str], None] | None = None,
    ) -> None:
        """初始化智能体

        Args:
            api_key: Anthropic API Key
            model: Claude 模型名称
            max_iterations: 最大迭代次数（防止无限循环）
            on_message: 消息回调，接收 (role, content) 用于实时展示
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_iterations = max_iterations
        self.on_message = on_message
        self.messages: list[dict[str, Any]] = []

    def _emit(self, role: str, content: str) -> None:
        """触发消息事件（用于实时日志/Web 展示）"""
        logger.info(f"[{role.upper()}] {content[:200]}{'...' if len(content) > 200 else ''}")
        if self.on_message:
            self.on_message(role, content)

    async def run_recon(self, mcp_session: ClientSession) -> str:
        """执行侦察阶段：查询赛题并返回结果

        Args:
            mcp_session: 已初始化的 MCP 会话

        Returns:
            侦察报告字符串
        """
        logger.info("=== 开始侦察阶段 ===")

        # 获取 MCP 工具并转换格式
        tools = await list_tools(mcp_session)
        anthropic_tools = tools_to_anthropic_format(tools)

        # 注入侦察技能提示词
        user_message = RECON_SKILL + "\n请立即开始：查询所有赛题，并输出完整的侦察报告。"
        self.messages = [{"role": "user", "content": user_message}]
        self._emit("user", user_message)

        # 智能体主循环
        final_response = ""
        for iteration in range(self.max_iterations):
            logger.debug(f"迭代轮次: {iteration + 1}/{self.max_iterations}")

            # 调用 Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=anthropic_tools,
                messages=self.messages,
            )

            logger.debug(f"Claude 响应 stop_reason: {response.stop_reason}")

            # 处理响应内容
            assistant_content = response.content
            self.messages.append({"role": "assistant", "content": assistant_content})

            # 提取并展示文本内容
            for block in assistant_content:
                if block.type == "text" and block.text:
                    self._emit("assistant", block.text)
                    final_response = block.text

            # 检查是否结束
            if response.stop_reason == "end_turn":
                logger.info("智能体完成任务")
                break

            # 处理工具调用
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in assistant_content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_use_id = block.id

                        self._emit("tool_call", f"调用工具: {tool_name}，参数: {json.dumps(tool_input, ensure_ascii=False)}")

                        try:
                            # 执行 MCP 工具调用
                            result = await call_tool(mcp_session, tool_name, tool_input)
                            # 提取文本内容
                            result_text = _extract_tool_result(result)
                            self._emit("tool_result", f"[{tool_name}] 结果: {result_text[:500]}")
                        except Exception as e:
                            result_text = f"工具调用失败: {e}"
                            logger.error(f"工具 {tool_name} 调用失败: {e}")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": result_text,
                        })

                # 将工具结果添加到消息历史
                self.messages.append({"role": "user", "content": tool_results})
            else:
                # 其他终止原因
                logger.warning(f"未知 stop_reason: {response.stop_reason}")
                break

        if iteration >= self.max_iterations - 1:
            logger.warning(f"达到最大迭代次数 {self.max_iterations}，强制停止")

        return final_response


def _extract_tool_result(result: Any) -> str:
    """从 MCP 工具调用结果中提取文本内容"""
    if result is None:
        return "无返回结果"

    # MCP CallToolResult 格式
    if hasattr(result, "content"):
        contents = result.content
        if isinstance(contents, list):
            parts = []
            for item in contents:
                if hasattr(item, "text"):
                    parts.append(item.text)
                elif hasattr(item, "data"):
                    parts.append(str(item.data))
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        return str(contents)

    return str(result)
