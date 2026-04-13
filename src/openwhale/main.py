"""OpenWhale 主入口 - 渗透测试智能体启动器"""

from __future__ import annotations

import asyncio
import os
import sys
import threading
from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .agents import create_agent
from .util.logging_config import setup_logging
from .util.mcp_client import create_mcp_session
from .web.app import broadcast_message, run as run_web

console = Console()


def _banner() -> None:
    """输出启动横幅"""
    banner = Text()
    banner.append("🐋 OpenWhale", style="bold cyan")
    banner.append("  渗透测试智能体 v0.1.0", style="dim")
    console.print(Panel(banner, border_style="cyan", padding=(0, 2)))


def _load_config() -> dict[str, str]:
    """从环境变量加载配置（支持 .env 文件）"""
    load_dotenv()

    server_host = os.getenv("SERVER_HOST", "")
    mcp_server_url = os.getenv("MCP_SERVER_URL", "")
    if not mcp_server_url and server_host:
        if server_host.startswith("http://") or server_host.startswith("https://"):
            mcp_server_url = f"{server_host.rstrip('/')}/mcp"
        else:
            mcp_server_url = f"http://{server_host.rstrip('/')}/mcp"

    model_api_key = os.getenv("TOKENHUB_API_KEY") or os.getenv("OPENAI_API_KEY", "")

    required_vars = {
        "AGENT_TOKEN": os.getenv("AGENT_TOKEN", ""),
        "SERVER_HOST": server_host,
        "MCP_SERVER_URL": mcp_server_url,
        "MODEL_API_KEY": model_api_key,
    }

    optional_vars = {
        "AGENT_BACKEND": os.getenv("AGENT_BACKEND", "openai_compat"),
        "MODEL_BASE_URL": os.getenv("MODEL_BASE_URL", "https://tokenhub.tencentmaas.com/v1"),
        "MODEL_NAME": os.getenv("MODEL_NAME", "MiniMax-M2.7"),
        "MODEL_ID": os.getenv("MODEL_ID", "ep-jsc7o0kw"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "WEB_HOST": os.getenv("WEB_HOST", "0.0.0.0"),
        "WEB_PORT": os.getenv("WEB_PORT", "8080"),
        "WEB_ENABLED": os.getenv("WEB_ENABLED", "true"),
    }

    config = {**required_vars, **optional_vars}

    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        console.print(
            f"[bold red]错误：缺少必需的环境变量: {', '.join(missing)}[/bold red]\n"
            "请复制 .env.example 为 .env 并填写相应配置。",
        )
        sys.exit(1)

    return config


async def _run_agent(config: dict[str, str]) -> None:
    """异步运行智能体主流程"""
    mcp_url = config["MCP_SERVER_URL"]
    agent_token = config["AGENT_TOKEN"]

    def on_message(role: str, content: str) -> None:
        """消息回调：转发给 Web 前端"""
        broadcast_message(role, content)

    agent = create_agent(config, on_message=on_message)

    broadcast_message(
        "system",
        "OpenWhale 启动 | "
        f"AgentBackend: {config['AGENT_BACKEND']} | MCP服务器: {mcp_url} | "
        f"模型: {config['MODEL_NAME']} ({config['MODEL_ID']}) | BaseURL: {config['MODEL_BASE_URL']}",
    )

    try:
        async with create_mcp_session(mcp_url, agent_token=agent_token) as mcp_session:
            logger.info("开始执行赛题流程...")
            broadcast_message("system", "开始执行赛题流程...")

            report = await agent.run_competition(mcp_session)

            logger.success("流程执行完成！")
            broadcast_message("system", "流程执行完成！")

            # 在控制台输出最终结果
            console.print(
                Panel(
                    report.final_message or "(模型未输出最终文本)",
                    title="[bold green]执行报告[/bold green]",
                    border_style="green",
                    padding=(1, 2),
                )
            )

    except Exception as e:
        logger.error(f"智能体运行失败: {e}")
        broadcast_message("system", f"错误: {e}")
        raise
    except KeyboardInterrupt:
        logger.warning("用户中断运行，已停止智能体")
        broadcast_message("system", "用户中断运行，已停止智能体")
        return


def main() -> None:
    """命令行入口"""
    _banner()

    # 加载配置
    config = _load_config()

    # 初始化日志
    setup_logging(config["LOG_LEVEL"])

    logger.info(
        "配置加载完成 | "
        f"AgentBackend: {config['AGENT_BACKEND']} | 模型: {config['MODEL_NAME']} ({config['MODEL_ID']}) | "
        f"BaseURL: {config['MODEL_BASE_URL']} | MCP: {config['MCP_SERVER_URL']}"
    )

    # 启动 Web 前端（后台线程）
    web_enabled = config["WEB_ENABLED"].lower() in ("1", "true", "yes")
    if web_enabled:
        web_thread = threading.Thread(
            target=run_web,
            kwargs={
                "host": config["WEB_HOST"],
                "port": int(config["WEB_PORT"]),
            },
            daemon=True,
        )
        web_thread.start()
        logger.info(f"Web 界面已启动: http://{config['WEB_HOST']}:{config['WEB_PORT']}")

    # 运行智能体
    asyncio.run(_run_agent(config))


if __name__ == "__main__":
    main()
