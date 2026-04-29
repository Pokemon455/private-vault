# 🤖 LangGraph Multi-Agent Chatbot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-Latest-orange?style=for-the-badge)
![FastMCP](https://img.shields.io/badge/FastMCP-MCP-purple?style=for-the-badge)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

> 🚀 A production-grade **Multi-Agent AI Chatbot** built with LangGraph — featuring intelligent routing, RAG, real-time web search, and Python code execution via MCP.

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔀 **Smart Router** | Automatically routes queries to the right tool (100% accuracy) |
| 🐍 **Python Executor** | Runs Python code in real-time via MCP server |
| 🔍 **Web Search** | Google search with full page content extraction (Apify) |
| 📄 **RAG System** | Document retrieval using Pinecone Vector DB + BM25 |
| 🧠 **Memory** | Persistent conversation memory via PostgreSQL (Neon) |
| 📊 **LangSmith** | Full observability and tracing |

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────┐
│ router_node │  ← Classifies: python_tool / web_search / rag / direct
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
LLM_Tool  answer_node
   │
   ▼
 tools  (run_python / web_search / RAG)
   │
   ▼
answer_node  ← Clean, language-aware response
   │
   ▼
  END
```

---

## 📁 Project Structure

```
├── langgraph_agent.py      # Main agent code
├── requirements.txt        # All dependencies
├── .env.example           # Environment variables template
├── config.py              # Configuration settings
├── docs/
│   ├── architecture.md    # Detailed architecture docs
│   └── api_reference.md   # API reference
├── tests/
│   └── test_agent.py      # Test cases
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Pokemon455/private-vault.git
cd private-vault
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Run
```python
import asyncio
from langgraph_agent import build_and_run

result = asyncio.get_event_loop().run_until_complete(
    build_and_run("python version check karo", thread_id="1")
)
print(result)
```

---

## 🔧 Configuration

| Variable | Description |
|----------|-------------|
| `NVIDIA_API_KEY` | NVIDIA NIM API key (LLM) |
| `PINECONE_API_KEY` | Pinecone Vector DB key |
| `LANGCHAIN_API_KEY` | LangSmith tracing key |
| `APIFY_API_TOKEN` | Web search API token |
| `DATABASE_URL` | PostgreSQL connection string |

---

## 🧪 Example Queries

```python
# Python tool
await build_and_run("python version check karo")
# → "Python 3.14.3 installed hai"

# Web search
await build_and_run("latest AI models 2026")
# → Real-time Google results

# Direct answer
await build_and_run("AI kya hota hai?")
# → Clean explanation

# RAG (after uploading a file)
await build_and_run("document mein kya hai?")
# → Retrieved from your document
```

---

## 📊 Router Accuracy

Tested on 10 diverse queries — **100% accuracy**

| Category | Examples | Accuracy |
|----------|----------|----------|
| `python_tool` | "numpy check karo", "code run karo" | ✅ 100% |
| `web_search` | "latest news", "Bitcoin price" | ✅ 100% |
| `rag` | "document mein..." | ✅ 100% |
| `direct` | "AI kya hai", "hello" | ✅ 100% |

---

## 🛠️ Tech Stack

- **LangGraph** — Multi-agent graph orchestration
- **LangChain** — LLM pipeline & tools
- **NVIDIA NIM** — LLM inference (gpt-oss-20b)
- **Pinecone** — Vector database for RAG
- **FastMCP** — Python code execution server
- **Apify** — Google search scraper
- **Neon PostgreSQL** — Conversation memory
- **LangSmith** — Observability & tracing

---

## 📈 Bugs Fixed

- ✅ Tool execution — tools node properly executes
- ✅ Hallucination — no history contamination in answer_node
- ✅ Language — Roman Urdu / English detection
- ✅ Loop — `tools → answer_node` directly (no infinite loop)

---

## 👨‍💻 Author

**Arbaz** — AI/ML Developer
- GitHub: [@Pokemon455](https://github.com/Pokemon455)
- Email: arwazrozi@gmail.com

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file
