# ── Imports ──────────────────────────────────────────────────────────────────
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage, ToolMessage
from langchain_core.tools import tool as tool_decorator
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader, Docx2txtLoader
from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Annotated, List
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import asyncio, os, requests
import nest_asyncio
nest_asyncio.apply()

# ── Environment ───────────────────────────────────────────────────────────────
os.environ["LANGCHAIN_PROJECT"]    = "my project"
os.environ["LANGCHAIN_API_KEY"]    = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["PINECONE_API_KEY"]     = "pcsk_7FpWKy_7UCkESDmyDDzzYEE2gHmP5bQDYfxXqV3NH9LuAaK2csFwNPioFMAcw5RpPz2PHa"

_BASE  = "https://integrate.api.nvidia.com/v1"
_KEY   = "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"
_MODEL = "openai/gpt-oss-20b"

# ── LLMs ─────────────────────────────────────────────────────────────────────
answer_LLM = ChatOpenAI(base_url=_BASE, api_key=_KEY, model=_MODEL)
router_LLM = ChatOpenAI(base_url=_BASE, api_key=_KEY, model=_MODEL, temperature=0)

# ── Embeddings ────────────────────────────────────────────────────────────────
class MockEmbeddings(Embeddings):
    def embed_documents(self, texts): return [[0.1] * 1024 for _ in texts]
    def embed_query(self, text):      return [0.1] * 1024

embeddings = MockEmbeddings()

# ── State & Schema ────────────────────────────────────────────────────────────
class RouterDecision(BaseModel):
    decision:  Literal["rag", "web_search", "python_tool", "direct"] = Field(description="Routing decision")
    reasoning: str = Field(min_length=5, max_length=200, description="Brief explanation")

class State(TypedDict):
    messages:        Annotated[List[BaseMessage], add_messages]
    file_uploaded:   bool
    router_decision: str
    reasoning:       str
    iteration_count: int

# ── Router Prompt ─────────────────────────────────────────────────────────────
ROUTER_PROMPT = """You are a routing assistant. Classify the query into one of:
- python_tool : code, python, packages, install, pip, version, environment, libraries, frameworks, "karo", "check karo", "chalao"
- rag         : user asking about uploaded file content. Keywords: "document", "file", "PDF", "report", "meri report", "is file mein", "uploaded", "mera data", "sheet", "spreadsheet"
- web_search  : news, weather, latest/newest/current/recent/today/aaj, real-time info, release dates, "kab release hoga", "kab aayega", price, stock
- direct      : general knowledge, definitions, greetings, simple questions (no code, no file, no real-time)

Rules:
- Any technical/code intent                              → python_tool
- "latest", "newest", "current", "kab release hoga"     → web_search
- ANY mention of "report", "file", "document", "PDF"    → rag
- Doubt between python_tool vs direct                   → python_tool
"""

# ── Document Loader ───────────────────────────────────────────────────────────
bm25_retriever = None

def load_document(file_path: str) -> str:
    loaders = {".pdf": PyPDFLoader, ".csv": CSVLoader, ".docx": Docx2txtLoader}
    ext = os.path.splitext(file_path)[1]
    if not os.path.exists(file_path):
        return "Error: File not found."
    if ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    elif ext in loaders:
        loader = loaders[ext](file_path)
    else:
        return "Error: Unsupported file format."
    docs = loader.load()
    if not docs:
        return "Warning: File is empty."
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(docs)
    global bm25_retriever
    bm25_retriever   = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = 2
    PineconeVectorStore.from_documents(chunks, embedding=embeddings, index_name="vector",
                                       pinecone_api_key=os.environ["PINECONE_API_KEY"])
    return f"Document stored. {len(chunks)} chunks."

# ── RAG Tool ──────────────────────────────────────────────────────────────────
@tool_decorator
def RAG(query: str) -> str:
    """Retrieve information from uploaded documents."""
    try:
        vs   = PineconeVectorStore(index_name="vector", embedding=embeddings,
                                   pinecone_api_key=os.environ["PINECONE_API_KEY"])
        docs = vs.as_retriever(search_type="mmr",
                               search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.7}).invoke(query)
        if not docs:
            return "No relevant documents found."
        return "".join(f"Source {i+1}: {d.page_content.strip()}\n\n" for i, d in enumerate(docs))
    except Exception as e:
        return f"Error: {e}"

# ── Web Search Tool ───────────────────────────────────────────────────────────
SKIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "menu"}
NAV_KW    = ["Log in","Sign up","Cookie","Subscribe","Newsletter",
             "Privacy","Terms","Click here","Skip to","Jump to","Edit link"]

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text, self.skip = [], False
    def handle_starttag(self, tag, attrs): self.skip = tag in SKIP_TAGS
    def handle_endtag(self, tag):          self.skip = False
    def handle_data(self, data):
        if not self.skip and data.strip(): self.text.append(data.strip())

def fetch_clean_content(url: str, max_chars: int = 1500):
    try:
        page = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        if any(w in page.text for w in ["Enable JavaScript","Just a moment","Cloudflare"]):
            return None
        p = TextExtractor()
        p.feed(page.text)
        raw       = " ".join(" ".join(p.text).split())
        sentences = [s.strip() for s in raw.split(".") if len(s.strip()) > 50]
        clean     = [s for s in sentences if not any(k.lower() in s.lower() for k in NAV_KW)]
        result    = ". ".join(clean[:15])[:max_chars]
        return result if len(result) > 100 else None
    except:
        return None

@tool_decorator
def web_search(query: str) -> str:
    """Search the web for current, real-time information."""
    try:
        resp = requests.post(
            "https://api.apify.com/v2/acts/apify~google-search-scraper/run-sync-get-dataset-items",
            params={"token": "apify_api_tSs2UiAGls0kg5v4PSorGGwi1blLJa3xTdmr"},
            json={"queries": query, "maxPagesPerQuery": 1, "resultsPerPage": 8,
                  "languageCode": "en", "countryCode": "us"},
            timeout=60
        )
        organic  = resp.json()[0].get("organicResults", [])
        if not organic: return "No results found."
        filtered = [r for r in organic if not any(
            s in r.get("url","") for s in ["youtube.com","reddit.com","twitter.com"])][:5]
        contents = list(ThreadPoolExecutor(3).map(
            fetch_clean_content, [r.get("url","") for r in filtered[:3]]))
        out = f"Search: '{query}'\n" + "="*50 + "\n\n"
        for i, r in enumerate(filtered):
            out += f"[{i+1}] {r.get('title','')}\n"
            out += f"Snippet: {r.get('description','').replace('Read more','').strip()}\n"
            if i < 3 and contents[i]: out += f"Content: {contents[i]}\n"
            out += "\n" + "-"*45 + "\n\n"
        return out
    except Exception as e:
        return f"Search error: {e}"

# ── MCP Client ────────────────────────────────────────────────────────────────
client = MultiServerMCPClient({
    "python_tool": {"transport": "streamable-http", "url": "https://deploy-9ugq.onrender.com/mcp"}
})

# ── Graph ─────────────────────────────────────────────────────────────────────
TOOL_MAP = {"python_tool": "run_python", "rag": "RAG", "web_search": "web_search"}
DB_URL   = "postgresql://neondb_owner:npg_2ZoGDQfIRm5c@ep-falling-wind-an7m70j5-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

async def build_and_run(query: str, thread_id: str = "1") -> str:
    mcp_tools = await asyncio.wait_for(client.get_tools(), timeout=30)
    all_tools  = [RAG, web_search, *mcp_tools]
    tool_node  = ToolNode(all_tools)

    async def router_node(state):
        try:
            r = await router_LLM.with_structured_output(RouterDecision).ainvoke([
                SystemMessage(content=ROUTER_PROMPT + f"\nfile_uploaded={state.get('file_uploaded', False)}"),
                HumanMessage(content=state["messages"][-1].content)
            ])
            return {"router_decision": r.decision, "reasoning": r.reasoning}
        except Exception as e:
            return {"router_decision": "direct", "reasoning": str(e)}

    def route_condition(state):
        return "LLM_Tool" if state["router_decision"] in TOOL_MAP else "answer_node"

    async def LLM_Tool(state):
        msgs  = state["messages"]
        dec   = state.get("router_decision")
        itr   = state.get("iteration_count", 0)
        if isinstance(msgs[-1], ToolMessage):
            return {"messages": [], "iteration_count": itr}
        forced = TOOL_MAP.get(dec)
        sp = f"""You are an AI assistant. Decision: {dec}.
STRICTLY call the tool: {forced}
- python_tool → run_python : write complete python code with print()
- rag         → RAG        : pass user question exactly
- web_search  → web_search : pass user question exactly
DO NOT answer in text. ONLY make a tool call."""
        resp = await answer_LLM.bind_tools(all_tools, tool_choice=forced).ainvoke(
            [SystemMessage(content=sp)] + msgs[-6:]
        )
        return {"messages": [resp], "iteration_count": itr + 1}

    def tool_condition(state):
        last = state["messages"][-1]
        itr  = state.get("iteration_count", 0)
        if itr >= 3:                                          return "answer_node"
        if isinstance(last, ToolMessage):                     return "answer_node"
        if isinstance(last, AIMessage) and last.tool_calls:  return "tools"
        return "answer_node"

    async def answer_node(state):
        msgs     = state["messages"]
        tool_out = next((m.content for m in reversed(msgs) if isinstance(m, ToolMessage)), None)
        user_q   = next((m.content for m in reversed(msgs) if isinstance(m, HumanMessage)), "")
        sp = """You are a helpful assistant.
- Reply in the SAME language as the user (Roman Urdu or English only, never Urdu/Hindi script)
- If tool result is available: explain in 2-3 simple lines
- If no tool result: answer from knowledge
- No filler words, no unnecessary repetition"""
        if tool_out:
            sp += f"\n\nTool result:\n{tool_out}"
        resp = await answer_LLM.ainvoke([SystemMessage(content=sp), HumanMessage(content=user_q)])
        return {"messages": [resp]}

    g = StateGraph(State)
    g.add_node("router_node", router_node)
    g.add_node("LLM_Tool",    LLM_Tool)
    g.add_node("tools",       tool_node)
    g.add_node("answer_node", answer_node)
    g.add_edge(START, "router_node")
    g.add_conditional_edges("router_node", route_condition, {"LLM_Tool": "LLM_Tool", "answer_node": "answer_node"})
    g.add_conditional_edges("LLM_Tool",    tool_condition,  {"tools": "tools",       "answer_node": "answer_node"})
    g.add_edge("tools",       "answer_node")
    g.add_edge("answer_node", END)

    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    async with AsyncPostgresSaver.from_conn_string(DB_URL) as cp:
        await cp.setup()
        bot = g.compile(checkpointer=cp)
        res = await bot.ainvoke(
            {"messages": [HumanMessage(content=query)], "file_uploaded": False, "iteration_count": 0},
            config={"configurable": {"thread_id": thread_id}}
        )
        return res["messages"][-1].content

# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = asyncio.get_event_loop().run_until_complete(
        build_and_run("python version check karo", thread_id="1")
    )
    print(result)
