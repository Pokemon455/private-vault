"""
Configuration settings for LangGraph Agent.
Load all settings from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────
NVIDIA_API_KEY  = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL    = os.getenv("NVIDIA_MODEL", "openai/gpt-oss-20b")

# ── Vector DB ────────────────────────────────────
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX   = os.getenv("PINECONE_INDEX", "vector")

# ── LangSmith ────────────────────────────────────
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "my project")

# ── Web Search ───────────────────────────────────
APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")

# ── Database ─────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

# ── MCP Server ───────────────────────────────────
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://deploy-9ugq.onrender.com/mcp")

# ── Agent Settings ───────────────────────────────
MAX_ITERATIONS    = 3
CHUNK_SIZE        = 1000
CHUNK_OVERLAP     = 100
RETRIEVER_K       = 5
RETRIEVER_FETCH_K = 20
