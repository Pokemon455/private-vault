# ============================================
# IMPORTS
# ============================================
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage, ToolMessage
from langchain_core.tools import tool as tool_decorator
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader, Docx2txtLoader, JSONLoader
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Annotated, List
from langchain_community.retrievers import BM25Retriever
from langchain_mcp_adapters.client import MultiServerMCPClient
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import asyncio, logging, os, requests, time
import nest_asyncio
nest_asyncio.apply()

# ============================================
# ENV VARIABLES
# ============================================
os.environ["LANGCHAIN_PROJECT"]    = "my project"
os.environ["LANGCHAIN_API_KEY"]    = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["PINECONE_API_KEY"]     = "pcsk_7FpWKy_7UCkESDmyDDzzYEE2gHmP5bQDYfxXqV3NH9LuAaK2csFwNPioFMAcw5RpPz2PHa"

logger = logging.getLogger(__name__)

# ============================================
# LLM
# ============================================
answer_LLM = ChatOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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",
    model="openai/gpt-oss-20b"
)

# ============================================
# MOCK EMBEDDINGS (no download needed)
# ============================================
class MockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.1] * 1024 for _ in texts]
    def embed_query(self, text):
        return [0.1] * 1024

embeddings = MockEmbeddings()

# ============================================
# STATE + MODELS
# ============================================
class RouterDecision(BaseModel):
    decision: Literal["rag", "web_search", "python_tool", "direct"] = Field(
        description="Routing decision based on query"
    )
    reasoning: str = Field(min_length=5, max_length=200, description="Brief explanation")

class State(TypedDict):
    messages:        Annotated[List[BaseMessage], add_messages]
    file_uploaded:   bool
    router_decision: str
    reasoning:       str
    iteration_count: int

bm25_retriever = None

# ============================================
# ROUTER PROMPT
# ============================================
ROUTER_PROMPT = """You are a routing assistant. Classify query into one of:
- python_tool: code, python, packages, install, pip, version, environment, libraries, frameworks, "karo", "check karo", "chalao"
- rag: user uploaded a file, asking about document content
- web_search: news, weather, latest/newest/current/recent/today/aaj, real-time info, newest model/version/release
- direct: general knowledge, definitions, greetings, simple questions (NO code, NO file, NO real-time)

Rules:
- Any technical/code intent → python_tool
- "latest", "newest", "current" product/model → web_search
- Doubt between python_tool vs direct → python_tool
"""

# ============================================
# DOCUMENT LOADER
# ============================================
def load_document(file_path: str):
    try:
        if not os.path.exists(file_path):
            return "Error: File not found."
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith(".csv"):
            loader = CSVLoader(file_path)
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
        elif file_path.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        else:
            return "Error: Unsupported file format."
        docs = loader.load()
        if not docs:
            return "Warning: File is empty."
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(docs)
        global bm25_retriever
        bm25_retriever = BM25Retriever.from_documents(chunks)
        bm25_retriever.k = 2
        vectorstore = PineconeVectorStore.from_documents(
            chunks, embedding=embeddings,
            index_name="vector",
            pinecone_api_key=os.environ["PINECONE_API_KEY"]
        )
        return f"Document stored successfully. {len(chunks)} chunks."
    except Exception as e:
        return f"Failed: {str(e)}"

# ============================================
# RAG TOOL
# ============================================
@tool_decorator
def RAG(query: str):
    """Use this tool to retrieve information from uploaded documents."""
    try:
        vectorstore = PineconeVectorStore(
            index_name="vector",
            embedding=embeddings,
            pinecone_api_key=os.environ["PINECONE_API_KEY"]
        )
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.7}
        )
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant documents found."
        return "".join([f"Source {i+1}: {doc.page_content.strip()}\n\n" for i, doc in enumerate(docs)])
    except Exception as e:
        return f"Error: {str(e)}"

# ============================================
# WEB SEARCH TOOL
# ============================================
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ["script","style","nav","footer","header","aside","menu"]:
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ["script","style","nav","footer","header","aside","menu"]:
            self.skip = False
    def handle_data(self, data):
        if not self.skip and data.strip():
            self.text.append(data.strip())

def fetch_clean_content(url, max_chars=1500):
    try:
        page = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        for wall in ["Enable JavaScript","Just a moment","Cloudflare","Please enable cookies"]:
            if wall in page.text: return None
        parser = TextExtractor()
        parser.feed(page.text)
        raw = " ".join(" ".join(parser.text).split())
        sentences = [s.strip() for s in raw.split(".") if len(s.strip()) > 50]
        nav_kw = ["Log in","Sign up","Cookie","Subscribe","Newsletter",
                  "Privacy","Terms","Click here","Skip to","Jump to","Edit link"]
        clean = [s for s in sentences if not any(k.lower() in s.lower() for k in nav_kw)]
        result = ". ".join(clean[:15])[:max_chars]
        return result if len(result) > 100 else None
    except:
        return None

def fetch_parallel(urls, max_workers=3):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fetch_clean_content, urls))

@tool_decorator
def web_search(query: str) -> str:
    """Search the web for current, real-time information using Google."""
    try:
        token = "apify_api_tSs2UiAGls0kg5v4PSorGGwi1blLJa3xTdmr"
        resp = requests.post(
            "https://api.apify.com/v2/acts/apify~google-search-scraper/run-sync-get-dataset-items",
            params={"token": token},
            json={"queries": query, "maxPagesPerQuery": 1,
                  "resultsPerPage": 8, "languageCode": "en", "countryCode": "us"},
            timeout=60
        )
        organic = resp.json()[0].get("organicResults", [])
        if not organic: return "No results found."
        filtered = [r for r in organic if not any(
            s in r.get("url","") for s in ["youtube.com","reddit.com","twitter.com"])][:5]
        contents = fetch_parallel([r.get("url","") for r in filtered[:3]])
        output = f"Search: '{query}'\n{\'=\'*50}\n\n"
        for i, r in enumerate(filtered):
            output += f"[{i+1}] {r.get(\'title\',\'\')}
"
            output += f"Snippet: {r.get(\'description\',\'\').replace(\'Read more\',\'\').strip()}
"
            if i < 3 and contents[i]: output += f"Content: {contents[i]}
"
            output += "
" + "-"*45 + "

"
        return output
    except Exception as e:
        return f"Search error: {str(e)}"

# ============================================
# MCP CLIENT
# ============================================
servers = {
    "python_tool": {
        "transport": "streamable-http",
        "url": "https://deploy-9ugq.onrender.com/mcp"
    }
}
client = MultiServerMCPClient(servers)

# ============================================
# MAIN GRAPH
# ============================================
async def build_and_run(query: str, thread_id: str = "1"):
    ct  = await asyncio.wait_for(client.get_tools(), timeout=30)
    _T  = [RAG, web_search, *ct]
    _TN = ToolNode(_T)

    async def router_node(state):
        try:
            q  = state["messages"][-1].content
            fu = state.get("file_uploaded", False)
            r  = await answer_LLM.with_structured_output(RouterDecision).ainvoke([
                SystemMessage(content=ROUTER_PROMPT + f"
file_uploaded={fu}"),
                HumanMessage(content=q)
            ])
            print(f"  Router → {r.decision} | {r.reasoning}")
            return {"router_decision": r.decision, "reasoning": r.reasoning}
        except Exception as e:
            return {"router_decision": "direct", "reasoning": str(e)}

    def route_condition(state):
        return "LLM_Tool" if state["router_decision"] in {"rag","web_search","python_tool"} else "answer_node"

    async def LLM_Tool(state):
        msgs   = state["messages"]
        dec    = state.get("router_decision")
        itr    = state.get("iteration_count", 0)
        forced = {"python_tool":"run_python","rag":"RAG","web_search":"web_search"}.get(dec)
        last   = msgs[-1]
        if isinstance(last, ToolMessage):
            return {"messages": [], "iteration_count": itr}
        sp = f"""You are an AI assistant. Decision: {dec}.
STRICTLY call the tool: {forced}
- python_tool → run_python: write complete python code with print()
- rag → RAG: pass user question exactly
- web_search → web_search: pass user question exactly
DO NOT answer in text. ONLY tool call."""
        kw   = {"tool_choice": forced} if forced else {}
        resp = await answer_LLM.bind_tools(_T, **kw).ainvoke(
            [SystemMessage(content=sp)] + msgs[-6:]
        )
        if resp.tool_calls:
            print(f"  Tool → {resp.tool_calls[0]['name']}")
        return {"messages": [resp], "iteration_count": itr + 1}

    def tool_condition(state):
        msgs = state["messages"]
        last = msgs[-1]
        itr  = state.get("iteration_count", 0)
        if itr >= 3:
            return "answer_node"
        if isinstance(last, ToolMessage):
            return "answer_node"
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tools"
        return "answer_node"

    async def answer_node(state):
        msgs     = state["messages"]
        tool_out = next((m.content for m in reversed(msgs) if isinstance(m, ToolMessage)), None)
        user_q   = next((m.content for m in reversed(msgs) if isinstance(m, HumanMessage)), "")
        sp = """You are a helpful assistant.
- Reply in SAME language as user (Roman Urdu or English only)
- NEVER use Hindi/Urdu script
- If tool result: explain in 2-3 simple lines
- If no tool result: answer from knowledge
- No extra words, no noise"""
        if tool_out:
            sp += f"

Tool result:
{tool_out}"
        resp = await answer_LLM.ainvoke([
            SystemMessage(content=sp),
            HumanMessage(content=user_q)
        ])
        return {"messages": [resp]}

    g = StateGraph(State)
    g.add_node("router_node", router_node)
    g.add_node("LLM_Tool",    LLM_Tool)
    g.add_node("tools",       _TN)
    g.add_node("answer_node", answer_node)
    g.add_edge(START, "router_node")
    g.add_conditional_edges("router_node", route_condition, {"LLM_Tool":"LLM_Tool","answer_node":"answer_node"})
    g.add_conditional_edges("LLM_Tool", tool_condition, {"tools":"tools","answer_node":"answer_node"})
    g.add_edge("tools", "answer_node")
    g.add_edge("answer_node", END)

    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    DB = "postgresql://neondb_owner:npg_2ZoGDQfIRm5c@ep-falling-wind-an7m70j5-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    async with AsyncPostgresSaver.from_conn_string(DB) as cp:
        await cp.setup()
        bot = g.compile(checkpointer=cp)
        res = await bot.ainvoke(
            {"messages": [HumanMessage(content=query)]},
            config={"configurable": {"thread_id": thread_id}}
        )
        return res["messages"][-1].content

# ============================================
# RUN - Query yahan likho
# ============================================
query     = "python version check karo"
thread_id = "1"

result = asyncio.get_event_loop().run_until_complete(
    build_and_run(query, thread_id)
)
print("\n" + "="*50)
print("FINAL ANSWER:")
print(result)
print("="*50)
