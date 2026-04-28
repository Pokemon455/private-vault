import streamlit as st

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ─── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 12px; }
    h1 { color: #00d4ff; text-align: center; }
    .subtitle { text-align: center; color: #888; margin-top: -15px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ─── Title ─────────────────────────────────────────────────────
st.title("🤖 AI Chatbot")
st.markdown('<p class="subtitle">Rule-Based Smart Assistant</p>', unsafe_allow_html=True)

# ─── Rule-Based Response Engine ────────────────────────────────
def get_response(user_input: str) -> str:
    msg = user_input.lower().strip()

    # Greetings
    if any(w in msg for w in ["hello", "hi", "hey", "salam", "assalam", "helo"]):
        return "👋 Hello! How can I help you today?"

    # How are you
    elif any(w in msg for w in ["how are you", "how r u", "kaisa ho", "kya haal"]):
        return "😊 I am doing great! Thanks for asking. How about you?"

    # Name
    elif any(w in msg for w in ["your name", "tera naam", "what are you", "who are you"]):
        return "🤖 I am an AI Chatbot built with Streamlit! I use rule-based logic to answer your questions."

    # Help
    elif any(w in msg for w in ["help", "madad", "support"]):
        return "🆘 Sure! I can help you with:\n- General questions\n- Greetings\n- Basic info\n- Fun facts\nJust type your question!"

    # Time
    elif any(w in msg for w in ["time", "waqt", "clock"]):
        from datetime import datetime
        now = datetime.now().strftime("%I:%M %p")
        return f"🕐 Current time is: **{now}**"

    # Date
    elif any(w in msg for w in ["date", "today", "aaj"]):
        from datetime import datetime
        today = datetime.now().strftime("%B %d, %Y")
        return f"📅 Today is: **{today}**"

    # Python
    elif any(w in msg for w in ["python", "programming", "code", "coding"]):
        return "🐍 Python is an amazing language! Great for AI, ML, web dev, and automation. Are you learning Python?"

    # AI / ML
    elif any(w in msg for w in ["ai", "artificial intelligence", "machine learning", "ml", "deep learning"]):
        return "🧠 AI & ML are the future! I myself am built using Python & Streamlit. Are you interested in AI?"

    # Weather
    elif any(w in msg for w in ["weather", "mausam", "rain", "sunny"]):
        return "☁️ I don't have live weather data, but you can check **weather.com** or Google for real-time updates!"

    # Joke
    elif any(w in msg for w in ["joke", "funny", "laugh", "mazak"]):
        return "😂 Why do programmers prefer dark mode?\n\nBecause **light attracts bugs!** 🐛"

    # Thank you
    elif any(w in msg for w in ["thanks", "thank you", "shukriya", "shukria"]):
        return "🙏 You're welcome! Happy to help anytime."

    # Bye
    elif any(w in msg for w in ["bye", "goodbye", "khuda hafiz", "alvida", "quit", "exit"]):
        return "👋 Goodbye! Have a great day! Come back anytime. 😊"

    # Age
    elif any(w in msg for w in ["your age", "how old", "kitna purana"]):
        return "🤖 I was just born recently! Age doesn't matter for bots 😄"

    # Creator
    elif any(w in msg for w in ["who made you", "creator", "developer", "kisne banaya", "author"]):
        return "👨‍💻 I was built by **Arbaz** — an AI/ML Developer. Check out his GitHub: [Pokemon455](https://github.com/Pokemon455)"

    # Fun fact
    elif any(w in msg for w in ["fact", "fun fact", "interesting", "tell me something"]):
        return "🌟 Fun Fact: The first computer bug was an actual bug — a moth found in a Harvard computer in 1947! 🦗"

    # Default
    else:
        return f"🤔 I'm not sure about **'{user_input}'**. Try asking about:\n- Greetings\n- Time & Date\n- Python / AI\n- Jokes\n- Fun Facts"

# ─── Chat History ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I am your AI Assistant. Ask me anything!"}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── User Input ────────────────────────────────────────────────
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get bot response
    response = get_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
