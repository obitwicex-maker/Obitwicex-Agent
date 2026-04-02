import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from datetime import datetime
import json

# --- 1. HUD & CENTER-CORE STYLING ---
st.set_page_config(page_title="OBITWICEX | AI_AGENT", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #050505; color: #00FF41; }
    .jarvis-orb-container { display: flex; justify-content: center; padding: 30px 0; width: 100%; }
    .jarvis-orb {
        width: 160px; height: 160px;
        background: radial-gradient(circle, #00FF41 0%, #001a07 70%);
        border-radius: 50%;
        box-shadow: 0 0 40px #00FF41, inset 0 0 40px #00FF41;
        animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 60px #00FF41; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }
    div[data-testid="stChatMessage"] { 
        background: linear-gradient(180deg, rgba(0, 255, 65, 0.1) 0%, rgba(0, 5, 0, 1) 100%);
        border: 1px solid #00FF41;
        border-radius: 5px; margin-bottom: 12px;
    }
    div[data-testid="stChatMessageAvatarUser"],
    div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .stMarkdown p { font-family: 'Fira Code', monospace; color: #00FF41 !important; }
    [data-testid="stSidebar"] { background-color: #050a05; border-right: 1px solid #1f3f1f; }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE BROWSER & TOOLS ---
def search_web(query):
    """Performs a live web search using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            return json.dumps(results)
    except Exception as e:
        return f"Search Error: {str(e)}"

def transcribe_voice(audio_file):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text
    except: return "VOICE_STREAM_AUTH_FAIL"

def agent_call(messages):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"].strip(),
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex AI"}
        )
        return client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=messages,
            stream=False # Stream False for tool use stability
        )
    except Exception as e:
        st.error(f"UPLINK_FAILURE: {str(e)}")
        return None

# --- 3. INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_OS")
    st.markdown(f"**TIME:** `{datetime.now().strftime('%H:%M:%S')}`")
    st.markdown("**STATUS:** `ENCRYPTED LIVE` 🟢")
    st.divider()
    st.subheader("🎙️ Voice Protocol")
    voice_input = st.audio_input("Speak Command...")
    if voice_input:
        with st.status("🔍 SYNCING...", expanded=False):
            st.session_state.voice_text = transcribe_voice(voice_input)

st.markdown('<div class="jarvis-orb-container"><div class="jarvis-orb"></div></div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    label = "USER" if message["role"] == "user" else "OBITWICEX_AGENT"
    with st.chat_message(message["role"]):
        st.markdown(f"**[{label}]**\n\n{message['content']}")

# --- 4. LOGIC ---
prompt = st.chat_input("Submit Command...")
if "voice_text" in st.session_state:
    prompt = st.session_state.voice_text
    del st.session_state.voice_text

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**[USER]**\n\n{prompt}")

    with st.chat_message("assistant"):
        # System instructions now tell the agent it can ask to 'SEARCH:'
        sys_msg = "You are Obitwicex AI Agent. If you need current info, start your reply with 'SEARCH: [query]'. Otherwise, chat normally."
        msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:]
        
        res = agent_call(msgs)
        if res:
            reply = res.choices[0].message.content
            
            # Browser Automation Logic: Check if Agent wants to search
            if reply.startswith("SEARCH:"):
                search_query = reply.replace("SEARCH:", "").strip("[] ")
                with st.spinner(f"🌐 BROWSER_LINK_ACTIVE: Searching {search_query}..."):
                    web_data = search_web(search_query)
                    # Feed search results back to the brain
                    msgs.append({"role": "assistant", "content": reply})
                    msgs.append({"role": "user", "content": f"Search Results: {web_data}"})
                    res = agent_call(msgs)
                    reply = res.choices[0].message.content

            st.markdown(f"**[OBITWICEX_AGENT]**\n\n{reply}")
            st.session_state.messages.append({"role": "assistant", "content": reply})
