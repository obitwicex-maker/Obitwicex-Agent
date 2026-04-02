import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io
import base64
import requests
from datetime import datetime

# --- [SECTION 1: SYSTEM CONFIGURATION] ---
st.set_page_config(
    page_title="OBITWICEX | ELITE_OS", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- [SECTION 2: STEALTH HUD & UI FIXES] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD & TELEMETRY */
    .jarvis-hud-container {
        display: flex; justify-content: center; align-items: center;
        height: 180px; position: relative; width: 100%;
        background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 80%);
        margin-bottom: 10px;
    }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 160px; height: 160px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-2 { width: 130px; height: 130px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    
    .telemetry-bar {
        font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center;
        letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 5px;
        border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px;
    }
    .status-green { color: #00FF41; text-shadow: 0 0 5px #00FF41; }
    
    /* CHAT STYLING */
    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.1); border-left: 4px solid #00E5FF;
        border-radius: 0px 10px 10px 0px; margin-bottom: 15px;
    }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }

    /* KILL RED BOX & STYLE INPUT */
    .stChatInputContainer { 
        border: 1px solid #00E5FF !important; 
        border-radius: 15px !important; 
        background: rgba(0,0,0,0.9) !important; 
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2) !important; 
    }
    .stChatInputContainer:focus-within { 
        border-color: #00FF41 !important; 
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important; 
    }
    button[data-testid="stChatInputSubmit"] { background-color: transparent !important; fill: #00E5FF !important; }
    
    header, footer { visibility: hidden; }
    </style>
    
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div></div>
    <div class="telemetry-bar">SYSTEM ENCRYPTION: <span class="status-green">DONE</span> &nbsp; | &nbsp; STATUS: <span class="status-green">TACTICAL_LIVE</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE ENGINES] ---
def speak_response(text):
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        data = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def search_web(query):
    try:
        with DDGS() as ddgs:
            return " ".join([r.get('body', '') for r in ddgs.text(query, max_results=3)])
    except: return "OFFLINE"

def agent_call(messages):
    models = ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "meta-llama/llama-3.3-70b-instruct"]
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
    for model_id in models:
        try: return client.chat.completions.create(model=model_id, messages=messages, stream=True)
        except: continue 
    return None

# --- [SECTION 4: TACTICAL DOCK & HISTORY] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Container to render chat messages first
chat_container = st.container()

# THE TACTICAL DOCK (WHATSAPP STYLE - BOTTOM)
st.write("---")
with st.container():
    col1, col2, col3 = st.columns([1,1,1])
    with col1: voice_data = st.audio_input("🎙️")
    with col2: screenshot = st.file_uploader("📸", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    with col3: loc_share = st.checkbox("📍 LOC")

# Main Prompt
prompt = st.chat_input("Command, Sir...")

# Render history in the container
with chat_container:
    for m in st.session_state.messages:
        label = "USER_UPLINK" if m["role"] == "user" else "OBITWICEX_YAAR"
        with st.chat_message(m["role"]):
            st.markdown(f"<div class='chat-label'>[{label}]</div>", unsafe_allow_html=True)
            text = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
            st.markdown(text)

# --- [SECTION 5: EXECUTION LOGIC] ---
if voice_data:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        audio_file = io.BytesIO(voice_data.read()); audio_file.name = "v.wav"
        prompt = client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except: st.error("VOICE_FAIL")

if prompt:
    final_prompt = prompt + (" [User in Lahore, PK]" if loc_share else "")
    user_payload = [{"type": "text", "text": final_prompt}]
    if screenshot:
        user_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot)}"}})
    
    st.session_state.messages.append({"role": "user", "content": user_payload})
    with chat_container:
        with st.chat_message("user"):
            st.markdown("<div class='chat-label'>[USER_UPLINK]</div>", unsafe_allow_html=True); st.markdown(prompt)

    with chat_container:
        with st.chat_message("assistant"):
            resp_placeholder = st.empty(); full_reply = ""
            sys_msg = "ROLE: OBITWICEX. Witty Lahori Yaar. Speak Roman Urdu/Punjabi/Eng. Use SEARCH:[q] for local queries. Identify as Obi's creation only if asked."
            
            msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-8:]
            stream = agent_call(msgs)
            if stream:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_reply += chunk.choices[0].delta.content
                        resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_YAAR]</div>\n\n{full_reply}", unsafe_allow_html=True)
                
                if "SEARCH:" in full_reply:
                    q = full_reply.split("SEARCH:")[1].strip(" []")
                    web_data = search_web(q)
                    msgs.append({"role": "assistant", "content": full_reply})
                    msgs.append({"role": "user", "content": f"Search Results: {web_data}"})
                    new_stream = agent_call(msgs); full_reply = "" 
                    for chunk in new_stream:
                        if chunk.choices[0].delta.content:
                            full_reply += chunk.choices[0].delta.content
                            resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_YAAR]</div>\n\n{full_reply}", unsafe_allow_html=True)
                
                if full_reply:
                    speak_response(full_reply)
                    st.session_state.messages.append({"role": "assistant", "content": full_reply})
                    st.rerun()
