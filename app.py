import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
from datetime import datetime
import io

# --- 1. HUD & CENTER-CORE STYLING ---
st.set_page_config(page_title="OBITWICEX | AI_AGENT", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #050505; color: #00FF41; }
    
    .jarvis-orb-container { display: flex; justify-content: center; padding: 40px 0; width: 100%; }
    .jarvis-orb {
        width: 180px; height: 180px;
        background: radial-gradient(circle, #00FF41 0%, #001a07 70%);
        border-radius: 50%;
        box-shadow: 0 0 40px #00FF41, inset 0 0 40px #00FF41;
        animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }

    div[data-testid="stChatMessage"] { 
        background: linear-gradient(180deg, rgba(0, 255, 65, 0.1) 0%, rgba(0, 5, 0, 1) 100%);
        border: 1px solid #00FF41;
        border-radius: 5px; margin-bottom: 15px;
    }
    
    div[data-testid="stChatMessageAvatarUser"],
    div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    
    .stMarkdown p { font-family: 'Fira Code', monospace; color: #00FF41 !important; font-size: 1.1rem; }
    [data-testid="stSidebar"] { background-color: #050a05; border-right: 1px solid #1f3f1f; }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE BROWSER ENGINE ---
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r.get('body', '') for r in ddgs.text(query, max_results=3)]
            return " ".join(results)
    except: return "TASK_LINK_OFFLINE"

# --- 3. VOICE ENGINE ---
def transcribe_voice(audio_bytes):
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input.wav"
        # Scrubbing keys for clean auth
        key = st.secrets["OPENAI_API_KEY"].strip().strip('"').strip("'")
        client = OpenAI(api_key=key)
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text
    except Exception: return "VOICE_STREAMS_OFFLINE"

def agent_stream(messages):
    try:
        or_key = st.secrets["OPENROUTER_API_KEY"].strip().strip('"').strip("'")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=or_key,
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex AI"}
        )
        return client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=messages,
            stream=True # SPEED BOOST ENABLED
        )
    except: return None

# --- 4. HUD INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_OS")
    st.markdown(f"**TIME:** `{datetime.now().strftime('%H:%M:%S')}`")
    st.markdown("**STATUS:** `ENCRYPTED LIVE` 🟢")
    st.divider()
    
    st.subheader("🎙️ Voice Protocol")
    voice_data = st.audio_input("Speak Command...")
    
    if voice_data:
        if "last_audio_id" not in st.session_state or st.session_state.last_audio_id != id(voice_data):
            with st.spinner("🔍 DECODING..."):
                transcript = transcribe_voice(voice_data.read())
                if transcript != "VOICE_STREAMS_OFFLINE":
                    st.session_state.voice_text = transcript
                    st.session_state.last_audio_id = id(voice_data)
                else: 
                    st.error("Auth Failure. OpenAI balance sync pending. Check in 15-30 mins.")

    if st.button("TERMINATE_SESSION"):
        st.session_state.messages = []
        if "voice_text" in st.session_state: del st.session_state.voice_text
        st.rerun()

# --- THE CENTER CORE ANIMATION ---
st.markdown('<div class="jarvis-orb-container"><div class="jarvis-orb"></div></div>', unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    label = "USER" if message["role"] == "user" else "OBITWICEX_AGENT"
    with st.chat_message(message["role"]):
        st.markdown(f"**[{label}]**\n\n{message['content']}")

# --- 5. COMMAND LOGIC ---
prompt = st.chat_input("Submit Command, Sir...")

# Handle Voice Input
if "voice_text" in st.session_state:
    prompt = st.session_state.voice_text
    del st.session_state.voice_text

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**[USER]**\n\n{prompt}")

    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        full_reply = ""
        
        # System instructions
        sys_msg = "You are Obitwicex AI Agent. Elite partner. Use Roman Urdu for chat. English for data. To search the web, say 'SEARCH: [query]'. Time: " + datetime.now().strftime('%H:%M')
        msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:]
        
        # Start Streaming response
        stream = agent_stream(msgs)
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    # Real-time typing effect
                    resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply} █")
            
            # Browser task logic
            if "SEARCH:" in full_reply:
                query = full_reply.split("SEARCH:")[1].strip(" []")
                with st.spinner(f"🌐 BROWSER_LINK_ACTIVE: Searching {query}..."):
                    web_data = search_web(query)
                    msgs.append({"role": "assistant", "content": full_reply})
                    msgs.append({"role": "user", "content": f"Results: {web_data}"})
                    new_stream = agent_stream(msgs)
                    full_reply = "" # Reset for final answer from web data
                    for chunk in new_stream:
                        if chunk.choices[0].delta.content:
                            full_reply += chunk.choices[0].delta.content
                            resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply} █")

            resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply}")
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
