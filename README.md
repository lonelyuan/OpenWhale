# 🐋 OpenWhale - 渗透测试智能体

基于 OpenAI 兼容 SDK 构建的渗透测试 AI 智能体，用于参加腾讯云黑客松智能渗透挑战赛。

## 功能特性

- 🤖 **多智能体分工**：支持"侦察-检测-利用"流程，基于主从模式协作
- 🔌 **MCP 协议接入**：通过标准 MCP 协议直接接入比赛平台
- 📊 **实时 Web 监控**：极简 Web 前端，实时展示智能体运行过程
- 📝 **完整日志追踪**：使用 loguru + rich，每次运行保存全量日志
- 🔒 **环境变量配置**：API Key 等敏感信息通过环境变量注入，避免硬编码

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv 安装依赖（推荐）
pip install uv
uv sync
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填写以下必填项：
# AGENT_TOKEN=<YOUR_AGENT_TOKEN>
# SERVER_HOST=<SERVER_HOST>
# AGENT_BACKEND=openai_compat
# TOKENHUB_API_KEY=<YOUR_LLM_API_KEY>
```

### 3. 运行智能体

```bash
uv run openwhale


# 仅启动 Web 界面
uv run openwhale-web
```

运行后：
- 智能体将自动连接 MCP 服务器，按比赛流程执行赛题并输出执行报告
- Web 界面在 `http://localhost:8080` 实时展示运行过程

## 项目结构

```
OpenWhale/
├── src/openwhale/
│   ├── main.py           # 主入口（启动器）
│   ├── agent.py          # 兼容导出（保留旧导入路径）
│   ├── agents/
│   │   ├── base.py       # 智能体基类与统一执行框架
│   │   ├── factory.py    # 智能体工厂
│   │   ├── openai_agent.py # OpenAI 兼容实现
│   │   └── prompts.py    # 共享提示词
│   ├── web/
│   │   ├── app.py        # Web 前端（FastAPI + SSE）
│   │   └── templates/
│   │       └── index.html
│   └── util/
│       ├── __init__.py
│       ├── mcp_client.py     # MCP 协议客户端
│       └── logging_config.py # 日志配置（loguru + rich）
├── logs/                 # 运行时自动创建的日志目录
├── .env.example          # 环境变量模板
├── pyproject.toml        # 项目依赖配置（uv）
└── README.md
```

## 环境变量说明

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `AGENT_TOKEN` | ✅ | - | 竞赛平台 Agent Token（MCP 鉴权） |
| `SERVER_HOST` | ✅ | - | 竞赛平台 Server Host（自动拼接 `/mcp`） |
| `TOKENHUB_API_KEY` | ✅ | - | OpenAI 兼容模型 API Key |
| `MCP_SERVER_URL` | ❌ | 自动拼接 | 可手动覆盖 MCP 地址 |
| `AGENT_BACKEND` | ❌ | `openai_compat` | 智能体基座实现选择 |
| `MODEL_BASE_URL` | ❌ | `https://tokenhub.tencentmaas.com/v1` | OpenAI 兼容模型网关地址 |
| `MODEL_NAME` | ❌ | `MiniMax-M2.7` | 模型展示名称 |
| `MODEL_ID` | ❌ | `ep-jsc7o0kw` | 实际调用的模型 ID |
| `LOG_LEVEL` | ❌ | `INFO` | 日志级别 |
| `WEB_ENABLED` | ❌ | `true` | 是否启动 Web 界面 |
| `WEB_HOST` | ❌ | `0.0.0.0` | Web 服务监听地址 |
| `WEB_PORT` | ❌ | `8080` | Web 服务端口 |

## 技术栈

- **运行时**：Python 3.12+ / [uv](https://github.com/astral-sh/uv)
- **AI 基座**：[OpenAI Python SDK](https://github.com/openai/openai-python)
- **MCP 协议**：[Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- **日志**：[loguru](https://github.com/Delgan/loguru) + [rich](https://github.com/Textualize/rich)
- **Web**：[FastAPI](https://fastapi.tiangolo.com/) + Server-Sent Events
