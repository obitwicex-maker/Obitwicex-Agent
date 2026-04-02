import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io
import base64
import requests

# --- [SECTION 1: SYSTEM CONFIGURATION] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide")

# --- [SECTION 2: FANCY NEON UI & STEALTH TELEMETRY] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* JARVIS HUD ANIMATION */
    .jarvis-hud { display: flex; justify-content: center; align-items: center; height: 180px; position: relative; margin-bottom: 10px; }
    .ring { position: absolute; border-radius: 50%; border: 2px solid transparent; }
    .ring-1 { width: 160px; height: 160px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 20px #00E5FF; }
    .ring-2 { width: 130px; height: 130px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    /* STEALTH TELEMETRY BAR (KEEPING YOUR REQUESTED STATUS) */
    .telemetry-bar {
        font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center;
        letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 8px;
        border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px;
    }
    .status-green { color: #00FF41; text-shadow: 0 0 8px #00FF41; font-weight: bold; }

    /* LUXURY NEON CHAT BUBBLES */
    div[data-testid="stChatMessage"] { 
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(0,229,255,0.02) 100%);
        backdrop-filter: blur(15px); border: 1px solid rgba(0, 229, 255, 0.15);
        border-radius: 15px; padding: 15px; margin-bottom: 20px; box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; 
                   margin-bottom: 10px; border-bottom: 1px solid rgba(0,229,255,0.1); padding-bottom: 5px; }
    
    header, footer { visibility: hidden; }
    </style>
    
    <div class="jarvis-hud"><div class="ring ring-1"></div><div class="ring ring-2"></div></div>
    
    <div class="telemetry-bar">
        SYSTEM ENCRYPTION: <span class="status-green">DONE</span> &nbsp; | &nbsp; 
        STATUS CHECK: <span class="status-green">LIVE</span> &nbsp; | &nbsp; 
        UPLINK: <span class="status-green">OPTIMAL</span>
    </div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE MULTILINGUAL ENGINE] ---
def speak(text):
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        data = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def agent_call(messages):
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
    try: return client.chat.completions.create(model="anthropic/claude-3.5-sonnet", messages=messages, stream=True)
    except: return None

# --- [SECTION 4: DUAL UPLINK INTERFACE] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Top Row: Multilingual Voice & Visual Scan
col1, col2 = st.columns([2,1])
with col1:
    voice_msg = st.audio_input("🎙️ VOICE MESSAGE (Urdu/Punjabi/Hindi/Finnish)")
with col2:
    scan = st.file_uploader("📸 SCAN", type=['png', 'jpg', 'jpeg'])

st.divider()

# Fancy Render
for m in st.session_state.messages:
    label = "USER_COMMAND" if m["role"] == "user" else "OBITWICEX_UPLINK"
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{label}]</div>", unsafe_allow_html=True)
        text = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
        st.markdown(text)

# Execution Flow
prompt = st.chat_input("Submit Command, Sir...")

# Handle Voice Input (Whisper Multi-Detection)
if voice_msg:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        audio_file = io.BytesIO(voice_msg.read()); audio_file.name = "v.wav"
        prompt = client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except: st.error("VOICE_UPLINK_FAIL")

if prompt:
    user_payload = [{"type": "text", "text": prompt}]
    if scan:
        b64_img = base64.b64encode(scan.read()).decode('utf-8')
        user_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}})
    
    st.session_state.messages.append({"role": "user", "content": user_payload})
    with st.chat_message("user"):
        st.markdown("<div class='chat-label'>[USER_COMMAND]</div>", unsafe_allow_html=True); st.markdown(prompt)

    with st.chat_message("assistant"):
        resp_placeholder = st.empty(); full_reply = ""
        sys_msg = """ROLE: OBITWICEX. Created by OBI. 
        IDENTITY: You are Obitwicex, built to show AI's POWER. AI performs, it doesn't just talk.
        MULTILINGUAL: You perfectly understand and speak English, Roman Urdu, Punjabi, Hindi, and Finnish. 
        PERSONALITY: Elite Lahori Yaar. Witty, sharp, and informal. 
        VOICE: Active. Speak all responses out loud."""
        
        msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-8:]
        stream = agent_call(msgs)
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_UPLINK]</div>\n\n{full_reply} █", unsafe_allow_html=True)
            
            speak(full_reply)
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
