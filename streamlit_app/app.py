import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# ─── Page Config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    .stTextInput input { background-color: #1a1a1a; color: white; border: 1px solid #333; }
    .stButton button { background-color: #00ff88; color: black; font-weight: bold; border-radius: 8px; }
    .user-msg { background-color: #1a1a1a; padding: 12px; border-radius: 10px; margin: 8px 0; color: white; border: 1px solid #333; }
    .bot-msg { background-color: #0d1f17; padding: 12px; border-radius: 10px; margin: 8px 0; color: #00ff88; border: 1px solid #1a3a2a; }
</style>
""", unsafe_allow_html=True)

# ─── Title ────────────────────────────────────────────────────────
st.title("🤖 AI Chatbot")
st.caption("Powered by LangChain + NVIDIA API")
st.divider()

# ─── LLM Setup ───────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    return ChatOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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",
        model="openai/gpt-oss-20b",
        max_tokens=500
    )

llm = get_llm()

# ─── Session State ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a helpful AI assistant. Be concise and friendly.")
    ]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─── Sidebar Tools ───────────────────────────────────────────────
with st.sidebar:
    st.header("🛠️ Tools")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [SystemMessage(content="You are a helpful AI assistant.")]
        st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    st.subheader("⚡ Quick Prompts")
    
    if st.button("Explain AI in simple words"):
        st.session_state.quick = "Explain AI in simple words"
    if st.button("Write a Python hello world"):
        st.session_state.quick = "Write a Python hello world program"
    if st.button("Tell me a fun fact"):
        st.session_state.quick = "Tell me an interesting fun fact"
    
    st.divider()
    st.caption("Built with LangChain + Streamlit")

# ─── Chat History Display ────────────────────────────────────────
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f'<div class="user-msg">👤 {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">🤖 {msg}</div>', unsafe_allow_html=True)

# ─── Input ───────────────────────────────────────────────────────
user_input = st.chat_input("Ask me anything...")

# Handle quick prompts
if hasattr(st.session_state, "quick"):
    user_input = st.session_state.quick
    del st.session_state.quick

# ─── Process Input ───────────────────────────────────────────────
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.messages.append(HumanMessage(content=user_input))
    
    with st.spinner("Thinking..."):
        response = llm.invoke(st.session_state.messages)
        reply = response.content
    
    st.session_state.messages.append(AIMessage(content=reply))
    st.session_state.chat_history.append(("bot", reply))
    st.rerun()
