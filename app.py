import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io, base64, requests

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CLEAN STEALTH CSS] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* CLEAN TOP HUD */
    .jarvis-hud { display: flex; justify-content: center; align-items: center; height: 140px; position: relative; width: 100%; margin-top: -30px; }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 120px; height: 120px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    .telemetry { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; background: rgba(0, 229, 255, 0.05); padding: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px; }

    /* CHAT BUBBLES */
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); border-left: 4px solid #00E5FF; border-radius: 0 10px 10px 0; margin-bottom: 10px; }
    
    /* FORCED DOCK STYLING - KILLS RED BORDER */
    .stChatInputContainer { border: 1px solid #00E5FF !important; border-radius: 12px !important; background: #000 !important; }
    .stChatInputContainer:focus-within { border-color: #00FF41 !important; box-shadow: 0 0 15px #00FF41 !important; }
    
    header, footer {visibility: hidden;}
    </style>
    
    <div class="jarvis-hud"><div class="ring ring-1"></div></div>
    <div class="telemetry">SYSTEM ENCRYPTION: <span style="color:#00FF41">DONE</span> | STATUS: <span style="color:#00FF41">TACTICAL_DOCK_ACTIVE</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE ENGINES] ---
def speak(text):
    try:
        # ElevenLabs 2026 Hardened API Call
        res = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM", 
            json={"text": text, "model_id": "eleven_multilingual_v2"}, 
            headers={"xi-api-key": st.secrets["ELEVENLABS_API_KEY"], "Content-Type": "application/json", "Accept": "audio/mpeg"})
        if res.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(res.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- [SECTION 4: THE UNIFIED DOCK (BOTTOM-ONLY)] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Container to render chat messages
chat_display = st.container()

# THE TACTICAL DOCK - FORCED BELOW CHAT
st.write("---")
dock = st.container()
with dock:
    # Creating a WhatsApp-style horizontal dock for media
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1: v_up = st.audio_input("🎙️")
    with col2: i_up = st.file_uploader("📸", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    with col3: l_up = st.checkbox("📍 LOC", value=False)

# Command Input sitting at the very bottom
prompt = st.chat_input("Command, Sir...")

# Logic to render chat history into the container
with chat_display:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m['content'][0]['text'] if isinstance(m['content'], list) else m['content'])

# --- [SECTION 5: EXECUTION LOGIC] ---
if v_up:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    prompt = client.audio.transcriptions.create(model="whisper-1", file=io.BytesIO(v_up.read())).text

if prompt:
    final_q = prompt + (" [User Location: Lahore, PK]" if l_up else "")
    payload = [{"type": "text", "text": final_q}]
    if i_up:
        payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(i_up.read()).decode()}"}})
    
    st.session_state.messages.append({"role": "user", "content": payload})
    
    with chat_display:
        with st.chat_message("assistant"):
            # Fixing OpenRouter 400 Bad Request with .strip()
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
            stream = client.chat.completions.create(model="anthropic/claude-3.5-sonnet", messages=[{"role":"system","content":"You are OBITWICEX, a witty Lahori Yaar."}]+st.session_state.messages[-6:], stream=True)
            full_reply = "".join([chunk.choices[0].delta.content for chunk in stream if chunk.choices[0].delta.content])
            st.markdown(full_reply)
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
            speak(full_reply)
            st.rerun()
