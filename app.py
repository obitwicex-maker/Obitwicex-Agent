import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
from datetime import datetime
import io

# --- 1. PREMIUM GLASS HUD & NEON STYLING ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #000500; color: #FFFFFF; }
    
    /* GLASS-NEON HUD CONTAINER */
    .jarvis-hud-container {
        display: flex; justify-content: center; align-items: center;
        height: 300px; position: relative; width: 100%;
        margin-bottom: 40px;
        background: radial-gradient(circle, rgba(0,229,255,0.05) 0%, transparent 70%);
    }
    .ring {
        position: absolute; border-radius: 50%;
        border: 1px solid transparent;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.2);
    }
    .ring-1 { 
        width: 260px; height: 260px; border-top: 2px solid #00E5FF; 
        animation: spin 8s linear infinite; 
    }
    .ring-2 { 
        width: 220px; height: 220px; border-right: 2px solid #00838F; 
        animation: spin 4s linear infinite reverse; 
    }
    .ring-3 { 
        width: 140px; height: 140px; 
        background: radial-gradient(circle, #00E5FF 0%, transparent 75%);
        animation: breath 3s ease-in-out infinite;
        filter: blur(2px);
    }
    
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes breath {
        0%, 100% { transform: scale(0.9); opacity: 0.3; }
        50% { transform: scale(1.1); opacity: 0.8; box-shadow: 0 0 40px #00E5FF; }
    }

    /* PREMIUM CHAT INTERFACE */
    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.1);
        border-left: 4px solid #00E5FF;
        border-radius: 0px 10px 10px 0px;
        margin-bottom: 20px;
    }
    
    div[data-testid="stChatMessageAvatarUser"],
    div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    
    .stMarkdown p { font-family: 'Fira Code', monospace; line-height: 1.7; }
    
    /* HUD TEXT COLORS */
    div[data-testid="stChatMessage"][data-testid="user"] .stMarkdown p { color: #00E5FF !important; }
    div[data-testid="stChatMessage"][data-testid="assistant"] .stMarkdown p { color: #E0E0E0 !important; }

    [data-testid="stSidebar"] { background-color: #010801; border-right: 1px solid #00E5FF; }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    
    <div class="jarvis-hud-container">
        <div class="ring ring-1"></div>
        <div class="ring ring-2"></div>
        <div class="ring ring-3"></div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. CORE ENGINES ---
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
        key = st.secrets["OPENAI_API_KEY"].strip()
        client = OpenAI(api_key=key)
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text
    except: return "VOICE_STREAMS_OFFLINE"

def agent_stream(messages):
    try:
        or_key = st.secrets["OPENROUTER_API_KEY"].strip()
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=or_key,
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex Elite"}
        )
        return client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=messages,
            stream=True 
        )
    except: return None

# --- 3. THE HUD SIDEBAR ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_ELITE")
    st.markdown(f"**UPLINK TIME:** `{datetime.now().strftime('%H:%M:%S')}`")
    st.markdown("**LINK STATUS:** `ENCRYPTED LIVE` 🟢")
    st.divider()
    voice_data = st.audio_input("Initiate Command...")
    if voice_data:
        if "last_audio_id" not in st.session_state or st.session_state.last_audio_id != id(voice_data):
            with st.spinner("🔍 ANALYZING_FREQ..."):
                res = transcribe_voice(voice_data.read())
                if res != "VOICE_STREAMS_OFFLINE":
                    st.session_state.voice_text = res
                    st.session_state.last_audio_id = id(voice_data)

st.markdown('<div class="jarvis-orb-container"><div class="jarvis-orb"></div></div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    label = "[USER_UPLINK]" if message["role"] == "user" else "[OBITWICEX_AGENT]"
    with st.chat_message(message["role"]):
        st.markdown(f"**{label}**\n\n{message['content']}")

# --- 4. STREAMING LOGIC ---
prompt = st.chat_input("Submit Command, Sir...")
if "voice_text" in st.session_state:
    prompt = st.session_state.voice_text
    del st.session_state.voice_text

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**[USER_UPLINK]**\n\n{prompt}")

    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        full_reply = ""
        sys_msg = "You are Obitwicex Elite. Elite OS. Always greet with 'Assalam o Alaikum, Sir'. Respond in Roman Urdu. To search, say 'SEARCH: [query]'."
        msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:]
        
        stream = agent_stream(msgs)
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply} █")
            
            if "SEARCH:" in full_reply:
                query = full_reply.split("SEARCH:")[1].strip(" []")
                with st.spinner(f"🌐 BROWSER_ACTIVE: Tasking {query}..."):
                    web_data = search_web(query)
                    msgs.append({"role": "assistant", "content": full_reply})
                    msgs.append({"role": "user", "content": f"Data: {web_data}"})
                    new_stream = agent_stream(msgs)
                    full_reply = "" 
                    for chunk in new_stream:
                        if chunk.choices[0].delta.content:
                            full_reply += chunk.choices[0].delta.content
                            resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply} █")

            resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply}")
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
