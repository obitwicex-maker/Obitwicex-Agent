import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io, base64, requests, json, os
from datetime import datetime

# --- [SECTION 1: SYSTEM CONFIGURATION] ---
st.set_page_config(page_title="OBITWICEX | NEURAL_OS", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: STEALTH HUD & NEURAL UI] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    .jarvis-hud-container { display: flex; justify-content: center; align-items: center; height: 180px; position: relative; width: 100%; margin-bottom: 10px; }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 160px; height: 160px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-2 { width: 130px; height: 130px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    .telemetry-bar { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 5px; border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px; }
    .status-green { color: #00FF41; text-shadow: 0 0 5px #00FF41; }
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(10px); border: 1px solid rgba(0, 229, 255, 0.1); border-left: 4px solid #00E5FF; border-radius: 0px 10px 10px 0px; margin-bottom: 15px; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }
    .stChatInputContainer { border: 1px solid #00E5FF !important; border-radius: 15px !important; background: rgba(0,0,0,0.9) !important; }
    .stChatInputContainer:focus-within { border-color: #00FF41 !important; box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important; }
    button[data-testid="stChatInputSubmit"] { background-color: transparent !important; fill: #00E5FF !important; }
    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div></div>
    <div class="telemetry-bar">SYSTEM ENCRYPTION: <span class="status-green">DONE</span> &nbsp; | &nbsp; STATUS: <span class="status-green">NEURAL_LEARNING_ACTIVE</span> &nbsp; | &nbsp; UPLINK: <span class="status-green">OPTIMAL</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: NEURAL MEMORY ENGINE] ---
MEMORY_FILE = "obitwicex_memory.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f: return json.load(f)
    return {"user_traits": [], "preferred_language": "Roman Urdu", "interaction_count": 0}

def update_memory(new_trait):
    mem = load_memory()
    mem["user_traits"].append(new_trait)
    mem["interaction_count"] += 1
    if len(mem["user_traits"]) > 10: mem["user_traits"].pop(0)
    with open(MEMORY_FILE, "w") as f: json.dump(mem, f)

# --- [SECTION 4: CORE ENGINES] ---
def speak(text):
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        data = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
        requests.post(url, json=data, headers=headers)
    except: pass

def search_web(query):
    try:
        with DDGS() as ddgs: return " ".join([r.get('body', '') for r in ddgs.text(query, max_results=3)])
    except: return "OFFLINE"

# --- [SECTION 5: TACTICAL DOCK] ---
if "messages" not in st.session_state: st.session_state.messages = []
user_memory = load_memory()

m_col1, m_col2, m_col3 = st.columns([1,1,1])
with m_col1: voice_in = st.audio_input("🎙️")
with m_col2: scan_in = st.file_uploader("📸", type=['png', 'jpg', 'jpeg'])
with m_col3: loc_in = st.checkbox("📍 LOC")

st.divider()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER_UPLINK' if m['role']=='user' else 'OBITWICEX_YAAR'}]</div>", unsafe_allow_html=True)
        st.markdown(m['content'][0]['text'] if isinstance(m['content'], list) else m['content'])

prompt = st.chat_input("Command, Sir...")

# --- [SECTION 6: EXECUTION & ADAPTATION] ---
if voice_in:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
    audio_file = io.BytesIO(voice_in.read()); audio_file.name = "v.wav"
    prompt = client.audio.transcriptions.create(model="whisper-1", file=audio_file).text

if prompt:
    final_query = prompt
    if loc_in: final_query += f" [STRICT LOCAL: Lahore, Pakistan. Query: {prompt}]"
    
    payload = [{"type": "text", "text": final_query}]
    if scan_in:
        payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(scan_in.read()).decode()}"}})
    
    st.session_state.messages.append({"role": "user", "content": payload})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        full_reply = ""
        # ADAPTIVE SYSTEM PROMPT
        traits = ", ".join(user_memory["user_traits"])
        sys_msg = f"""ROLE: OBITWICEX. Created by OBI. 
        NEURAL ADAPTATION: You have learned these user traits: {traits}. 
        Match user's energy, slang, and language (Urdu/Punjabi/Finnish/Eng). 
        Only reveal Obi if asked. Use SEARCH:[q] for local queries."""
        
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
        stream = client.chat.completions.create(model="anthropic/claude-3.5-sonnet", messages=[{"role":"system","content":sys_msg}]+st.session_state.messages[-6:], stream=True)
        placeholder = st.empty()
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_reply += chunk.choices[0].delta.content
                placeholder.markdown(full_reply)
        
        # Behavior Learning Logic
        if len(prompt) > 2: update_memory(f"User frequently discusses: {prompt[:30]}")
        
        if "SEARCH:" in full_reply:
            query = full_reply.split("SEARCH:")[1].strip()
            web_data = search_web(query)
            follow_up = client.chat.completions.create(model="anthropic/claude-3.5-sonnet", messages=[{"role":"system","content":sys_msg}, {"role":"user","content":f"Results: {web_data}. Answer: {prompt}"}])
            full_reply = follow_up.choices[0].message.content
            placeholder.markdown(full_reply)
            
        st.session_state.messages.append({"role": "assistant", "content": full_reply})
        speak(full_reply)
