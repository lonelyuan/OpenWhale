# 🐋 OpenWhale - 渗透测试智能体

基于 Claude SDK 构建的渗透测试 AI 智能体，用于参加腾讯云黑客松智能渗透挑战赛。

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

# 或直接安装
uv pip install -e .
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填写以下必填项：
# ANTHROPIC_API_KEY=sk-ant-...
# MCP_SERVER_URL=http://<SERVER_HOST>/mcp
```

### 3. 运行智能体

```bash
# 方式一：通过 uv run 运行（推荐）
uv run openwhale

# 方式二：直接运行模块
uv run python -m openwhale.main

# 仅启动 Web 界面
uv run openwhale-web
```

运行后：
- 智能体将自动连接 MCP 服务器，查询赛题并输出侦察报告
- Web 界面在 `http://localhost:8080` 实时展示运行过程

## 项目结构

```
OpenWhale/
├── src/openwhale/
│   ├── main.py           # 主入口（启动器）
│   ├── agent.py          # Claude 智能体（主从模式）
│   ├── mcp_client.py     # MCP 协议客户端
│   ├── logging_config.py # 日志配置（loguru + rich）
│   └── web/
│       ├── app.py        # Web 前端（FastAPI + SSE）
│       └── templates/
│           └── index.html
├── logs/                 # 运行时自动创建的日志目录
├── .env.example          # 环境变量模板
├── pyproject.toml        # 项目依赖配置（uv）
└── README.md
```

## 环境变量说明

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `ANTHROPIC_API_KEY` | ✅ | - | Anthropic Claude API 密钥 |
| `MCP_SERVER_URL` | ✅ | - | 竞赛 MCP 服务器地址 |
| `CLAUDE_MODEL` | ❌ | `claude-opus-4-5` | 使用的 Claude 模型 |
| `LOG_LEVEL` | ❌ | `INFO` | 日志级别 |
| `WEB_ENABLED` | ❌ | `true` | 是否启动 Web 界面 |
| `WEB_HOST` | ❌ | `0.0.0.0` | Web 服务监听地址 |
| `WEB_PORT` | ❌ | `8080` | Web 服务端口 |

## 技术栈

- **运行时**：Python 3.12+ / [uv](https://github.com/astral-sh/uv)
- **AI 基座**：[Anthropic Claude SDK](https://github.com/anthropics/anthropic-sdk-python)
- **MCP 协议**：[Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- **日志**：[loguru](https://github.com/Delgan/loguru) + [rich](https://github.com/Textualize/rich)
- **Web**：[FastAPI](https://fastapi.tiangolo.com/) + Server-Sent Events
