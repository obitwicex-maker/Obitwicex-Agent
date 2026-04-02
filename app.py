import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
from datetime import datetime
import io

# --- 1. JARVIS HUD & TERMINAL STYLING ---
st.set_page_config(page_title="OBITWICEX | JARVIS_OS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #050505; color: #00FF41; }
    
    /* JARVIS TRIPLE-RING HUD */
    .jarvis-hud-container {
        display: flex; justify-content: center; align-items: center;
        height: 300px; position: relative; width: 100%;
        margin-bottom: 20px;
    }
    .ring {
        position: absolute; border-radius: 50%;
        border: 2px solid transparent;
        border-top: 2px solid #00FF41;
        border-bottom: 2px solid #00FF41;
        animation: spin 3s linear infinite;
    }
    .ring-1 { width: 220px; height: 220px; animation-duration: 5s; opacity: 0.8; }
    .ring-2 { width: 180px; height: 180px; animation-duration: 3s; animation-direction: reverse; opacity: 0.6; }
    .ring-3 { 
        width: 120px; height: 120px; 
        background: radial-gradient(circle, rgba(0,255,65,0.4) 0%, transparent 70%);
        animation: pulse 2s ease-in-out infinite;
        border: none;
    }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes pulse {
        0%, 100% { transform: scale(0.9); opacity: 0.5; box-shadow: 0 0 20px #00FF41; }
        50% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 60px #00FF41; }
    }

    /* CHAT HUD BOXES */
    div[data-testid="stChatMessage"] { 
        background: linear-gradient(180deg, rgba(0, 255, 65, 0.08) 0%, rgba(0, 5, 0, 1) 100%);
        border: 1px solid #00FF41;
        border-radius: 5px; margin-bottom: 15px;
    }
    div[data-testid="stChatMessageAvatarUser"],
    div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    
    .stMarkdown p { font-family: 'Fira Code', monospace; color: #00FF41 !important; font-size: 1.1rem; line-height: 1.6; }
    [data-testid="stSidebar"] { background-color: #050a05; border-right: 1px solid #1f3f1f; }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    
    <div class="jarvis-hud-container">
        <div class="ring ring-1"></div>
        <div class="ring ring-2"></div>
        <div class="ring ring-3"></div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. CORE ENGINES (Voice & Browser) ---
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r.get('body', '') for r in ddgs.text(query, max_results=3)]
            return " ".join(results)
    except: return "TASK_LINK_OFFLINE"

def transcribe_voice(audio_bytes):
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input.wav"
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
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex JARVIS"}
        )
        return client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=messages,
            stream=True 
        )
    except: return None

# --- 3. THE SIDEBAR HUD ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_OS")
    st.markdown(f"**SYSTEM TIME:** `{datetime.now().strftime('%H:%M:%S')}`")
    st.success("STATUS: ENCRYPTED LIVE 🟢")
    st.divider()
    
    st.subheader("🎙️ Voice Protocol")
    voice_data = st.audio_input("Command via Voice...")
    
    if voice_data:
        if "last_audio_id" not in st.session_state or st.session_state.last_audio_id != id(voice_data):
            with st.spinner("🔍 DECODING_AUDIO..."):
                transcript = transcribe_voice(voice_data.read())
                if transcript != "VOICE_STREAMS_OFFLINE":
                    st.session_state.voice_text = transcript
                    st.session_state.last_audio_id = id(voice_data)
                else: 
                    st.error("Auth Failure. Verify OpenAI Balance.")

    if st.button("TERMINATE_SESSION"):
        st.session_state.messages = []
        if "voice_text" in st.session_state: del st.session_state.voice_text
        st.rerun()

# --- 4. CHAT DISPLAY ---
for message in st.session_state.messages:
    label = "USER" if message["role"] == "user" else "OBITWICEX_AGENT"
    with st.chat_message(message["role"]):
        st.markdown(f"**[{label}]**\n\n{message['content']}")

# --- 5. LOGIC & STREAMING ---
prompt = st.chat_input("Submit Command, Sir...")

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
        
        # SYSTEM PROTOCOL: Salam Greeting & Roman Urdu Logic
        sys_msg = """
        You are Obitwicex JARVIS. An elite AI Agent.
        1. Always greet with 'Assalam o Alaikum, Sir' or 'Salam, Sir'.
        2. NEVER use Namaste. 
        3. Respond in Roman Urdu for conversation. Use English for data/technical info.
        4. To search the web, say 'SEARCH: [query]'.
        """
        msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:]
        
        stream = agent_stream(msgs)
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply} █")
            
            # Browser task logic
            if "SEARCH:" in full_reply:
                query = full_reply.split("SEARCH:")[1].strip(" []")
                with st.spinner(f"🌐 BROWSER_LINK_ACTIVE: Searching {query}..."):
                    web_data = search_web(query)
                    msgs.append({"role": "assistant", "content": full_reply})
                    msgs.append({"role": "user", "content": f"Results: {web_data}"})
                    new_stream = agent_stream(msgs)
                    full_reply = "" 
                    for chunk in new_stream:
                        if chunk.choices[0].delta.content:
                            full_reply += chunk.choices[0].delta.content
                            resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply} █")

            resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply}")
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
