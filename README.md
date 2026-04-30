# 🤖 LangGraph Multi-Agent Chatbot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-0.3%2B-green?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen?style=for-the-badge)

> A production-grade **Multi-Agent AI Chatbot** built with LangGraph — featuring intelligent routing, RAG pipeline, real-time web search, Python code execution via MCP, and persistent memory.

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔀 **Smart Router** | Classifies every query and sends it to the right tool automatically |
| 🐍 **Python Executor** | Runs Python code in real-time via a remote MCP server |
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
  ┌────┴─────┐
  │          │
  ▼          ▼
llm_tool  answer_node
  │
  ▼
tool_exec  (run_python / search_web / RAG)
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
git clone https://github.com/Pokemon455/private-vault.git
cd private-vault
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
| `MCP_SERVER_URL` | Python executor | [fastmcp](https://github.com/Pokemon455/fastmcp-python-repl-server) |

---

## 🧪 Example Usage

```python
# Python code execution
await build_and_run("1 se 10 tak sum nikalo", thread_id="u1")
# → "Sum 55 hai"

# Real-time web search
await build_and_run("latest AI models 2026", thread_id="u1")
# → Live Google results

# General knowledge
await build_and_run("AI kya hota hai?", thread_id="u1")
# → Clean explanation in Roman Urdu

# Document Q&A (after calling load_document())
await build_and_run("document mein kya likha hai?", thread_id="u1")
# → Retrieved from your file
```

---

## 🗺️ Router Accuracy

Tested on 20+ queries — **100% routing accuracy**

| Route | Triggers |
|-------|---------|
| `python_tool` | code, python, install, pip, version, "karo", "chalao" |
| `web_search` | latest, news, today, current, price, stock |
| `rag` | file, document, PDF, report, uploaded |
| `direct` | greetings, definitions, general knowledge |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangGraph |
| LLM | NVIDIA NIM (gpt-oss-20b) |
| Vector DB | Pinecone |
| Code Execution | FastMCP (remote Python REPL) |
| Web Search | Apify Google Scraper |
| Memory | Neon PostgreSQL |
| Tracing | LangSmith |

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/test_agent.py -v
```

---

## 👨‍💻 Author

**Arbaz** — AI/ML Developer
GitHub: [@Pokemon455](https://github.com/Pokemon455)

---

## 📄 License

MIT — see [LICENSE](LICENSE)
