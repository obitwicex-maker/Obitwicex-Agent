import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io, base64, requests, json, os

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CSS - KILLING THE RED BORDER & TOP BUTTONS] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD & TELEMETRY - CLEAN TOP SECTION */
    .jarvis-hud-container { display: flex; justify-content: center; align-items: center; height: 160px; position: relative; width: 100%; margin-bottom: 5px; }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 140px; height: 140px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-2 { width: 110px; height: 110px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    .telemetry-bar { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 5px; border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 10px; }
    .status-green { color: #00FF41; text-shadow: 0 0 5px #00FF41; }

    /* CHAT BUBBLES */
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(10px); border: 1px solid rgba(0, 229, 255, 0.1); border-left: 4px solid #00E5FF; border-radius: 0px 10px 10px 0px; margin-bottom: 15px; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }

    /* TACTICAL INPUT BAR (NO RED BORDER) */
    .stChatInputContainer { border: 1px solid #00E5FF !important; border-radius: 12px !important; background: rgba(0,0,0,0.95) !important; box-shadow: 0 0 10px rgba(0, 229, 255, 0.2) !important; }
    .stChatInputContainer:focus-within { border-color: #00FF41 !important; box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important; }
    button[data-testid="stChatInputSubmit"] { background-color: transparent !important; fill: #00E5FF !important; }
    
    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div></div>
    <div class="telemetry-bar">SYSTEM ENCRYPTION: <span class="status-green">DONE</span> &nbsp; | &nbsp; STATUS: <span class="status-green">TACTICAL_LIVE</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE ENGINES - FIXED VOICE] ---
def speak(text):
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"]
        voice_id = "21m00Tcm4TlvDq8ikWAM" 
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        data = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
        res = requests.post(url, json=data, headers=headers)
        if res.status_code == 200:
            b64 = base64.b64encode(res.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def search_web(q):
    try:
        with DDGS() as ddgs: return " ".join([r.get('body', '') for r in ddgs.text(q, max_results=3)])
    except: return "OFFLINE"

# --- [SECTION 4: CHAT HISTORY & TACTICAL DOCK] ---
if "messages" not in st.session_state: st.session_state.messages = []

# DISPLAY CHAT HISTORY
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER_UPLINK' if m['role']=='user' else 'OBITWICEX_YAAR'}]</div>", unsafe_allow_html=True)
        st.markdown(m['content'][0]['text'] if isinstance(m['content'], list) else m['content'])

# THE DOCK (WHATSAPP STYLE - BOTTOM)
st.write("---")
dock_col1, dock_col2, dock_col3 = st.columns([1,1,1])
with dock_col1: v_up = st.audio_input("🎙️ RECORD")
with dock_col2: i_up = st.file_uploader("📸 SCAN", type=['png', 'jpg', 'jpeg'])
with dock_col3: l_up = st.checkbox("📍 LOC")

prompt = st.chat_input("Command, Sir...")

# --- [SECTION 5: LOGIC] ---
if v_up:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
    audio_file = io.BytesIO(v_up.read()); audio_file.name = "v.wav"
    prompt = client.audio.transcriptions.create(model="whisper-1", file=audio_file).text

if prompt:
    final_q = prompt
    if l_up: final_q += " [USER LOC: Lahore, PK. Provide nearby results for this context.]"
    
    payload = [{"type": "text", "text": final_q}]
    if i_up: payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(i_up.read()).decode()}"}})
    
    st.session_state.messages.append({"role": "user", "content": payload})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        full_reply = ""
        sys_msg = "ROLE: OBITWICEX. Witty Lahori. Multilingual. Only reveal Obi if asked. Use SEARCH:[q] for local info."
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
        stream = client.chat.completions.create(model="anthropic/claude-3.5-sonnet", messages=[{"role":"system","content":sys_msg}]+st.session_state.messages[-6:], stream=True)
        placeholder = st.empty()
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_reply += chunk.choices[0].delta.content
                placeholder.markdown(full_reply)
        
        if "SEARCH:" in full_reply:
            query = full_reply.split("SEARCH:")[1].strip()
            web_data = search_web(query)
            follow_up = client.chat.completions.create(model="anthropic/claude-3.5-sonnet", messages=[{"role":"system","content":sys_msg}, {"role":"user","content":f"Data: {web_data}. Answer: {prompt}"}])
            full_reply = follow_up.choices[0].message.content
            placeholder.markdown(full_reply)

        st.session_state.messages.append({"role": "assistant", "content": full_reply})
        speak(full_reply)
