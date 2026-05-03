# 🤖 LangGraph Multi-Agent Chatbot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-0.3%2B-green?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-orange?style=for-the-badge)
![FastMCP](https://img.shields.io/badge/FastMCP-0.2%2B-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen?style=for-the-badge)

> A production-grade **Multi-Agent AI Chatbot** built with LangGraph — featuring intelligent routing, RAG pipeline, real-time web search, Python code execution via MCP, and persistent memory backed by PostgreSQL.

**[⭐ Star this repo if it helps you!](#)**

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔀 **Smart Router** | Classifies every query and sends it to the right agent automatically |
| 🐍 **Python Executor** | Runs Python code in real-time via a remote FastMCP server |
| 🔍 **Web Search** | Google search with full page content extraction (Apify) |
| 📄 **RAG Pipeline** | Document Q&A using Pinecone Vector DB + BM25 hybrid retrieval |
| 🧠 **Persistent Memory** | Multi-thread conversation memory backed by PostgreSQL (Neon) |
| 📊 **Observability** | Full tracing via LangSmith |
| 🌐 **Bilingual** | Responds in Roman Urdu or English based on user language |

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────┐
│ router_node │  Classifies → python_tool / web_search / rag / direct
└──────┬──────┘
       │
  ┌────┴──────────┬──────────────┐
  ▼               ▼              ▼
python_tool    web_search      rag
(FastMCP)      (Apify)      (Pinecone)
       │
       ▼
  answer_node → END
```

---

## 📁 Project Structure

```
├── langgraph_agent.py   # Main agent — graph, nodes, tools
├── config.py            # All settings loaded from .env
├── requirements.txt     # Dependencies
├── .env.example         # Environment variables template
├── docs/
│   ├── architecture.md  # Deep-dive architecture docs
│   └── api_reference.md # API reference
├── tests/
│   └── test_agent.py    # pytest test suite
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/Pokemon455/langgraph-multi-agent.git
cd langgraph-multi-agent
pip install -r requirements.txt
```

### 2. Set up environment

```bash
cp .env.example .env
# Open .env and fill in your API keys
```

### 3. Run

```python
import asyncio
from langgraph_agent import build_and_run

result = asyncio.run(build_and_run("python version check karo", thread_id="1"))
print(result)
```

---

## 🔧 Required Environment Variables

| Variable | Description | Get it from |
|----------|-------------|-------------|
| `NVIDIA_API_KEY` | LLM inference | [build.nvidia.com](https://build.nvidia.com) |
| `PINECONE_API_KEY` | Vector database | [pinecone.io](https://pinecone.io) |
| `DATABASE_URL` | PostgreSQL memory | [neon.tech](https://neon.tech) |
| `APIFY_API_TOKEN` | Web search | [apify.com](https://apify.com) |
| `LANGCHAIN_API_KEY` | Tracing (optional) | [smith.langchain.com](https://smith.langchain.com) |
| `MCP_SERVER_URL` | FastMCP Python REPL | [fastmcp-python-repl-server](https://github.com/Pokemon455/fastmcp-python-repl-server) |

---

## 🔗 Related Projects

- [fastmcp-python-repl-server](https://github.com/Pokemon455/fastmcp-python-repl-server) — The MCP Python REPL server used by this agent
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) — The graph framework powering this project
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) — MCP integration for LangChain

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT © [Arbaz](https://github.com/Pokemon455)
