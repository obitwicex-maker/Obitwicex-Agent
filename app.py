import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io, base64, requests

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CUSTOM BLUE INLINE CSS] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD & CLEAN TOP */
    .jarvis-hud { display: flex; justify-content: center; align-items: center; height: 160px; margin-top: -30px; }
    .ring-1 { width: 120px; height: 120px; border: 2px solid #00E5FF; border-radius: 50%; border-top-color: transparent; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    .telemetry { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; background: rgba(0, 229, 255, 0.05); padding: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px; }

    /* CHAT LABELS */
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); border-left: 4px solid #00E5FF; border-radius: 0 10px 10px 0; margin-bottom: 10px; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }

    /* THE BLUE INLINE DOCK FIX */
    .stChatInputContainer { 
        border: 1px solid #00E5FF !important; 
        border-radius: 12px !important; 
        background: rgba(0, 229, 255, 0.02) !important; 
    }
    .stChatInputContainer:focus-within { 
        border-color: #00FF41 !important; 
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4) !important; 
    }
    
    /* ICON BUTTON STYLING (THE BLUE THEME) */
    .stCheckbox label span { color: #00E5FF !important; font-weight: bold; }
    .stFileUploader label { display: none; }
    div[data-testid="stFileUploader"] { margin-bottom: -15px; }
    
    /* AUDIO INPUT BUTTON THEME */
    section[data-testid="stAudioInput"] button {
        background-color: rgba(0, 229, 255, 0.1) !important;
        border: 1px solid #00E5FF !important;
        color: #00E5FF !important;
    }

    header, footer {visibility: hidden;}
    </style>
    
    <div class="jarvis-hud"><div class="ring-1"></div></div>
    <div class="telemetry">SYSTEM ENCRYPTION: <span style="color:#00FF41">DONE</span> | STATUS: <span style="color:#00FF41">BLUE_DOCK_ARMED</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: ENGINES] ---
def speak(text):
    try:
        res = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR", 
            json={"text": text, "model_id": "eleven_multilingual_v2"}, 
            headers={"xi-api-key": st.secrets["ELEVENLABS_API_KEY"], "Content-Type": "application/json", "Accept": "audio/mpeg"})
        if res.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(res.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- [SECTION 4: THE BLUE INLINE DOCK] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Show history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER_UPLINK' if m['role']=='user' else 'OBITWICEX_YAAR'}]</div>", unsafe_allow_html=True)
        st.markdown(m['content'][0]['text'] if isinstance(m['content'], list) else m['content'])

# THE TACTICAL DOCK (BLUE ICONS BEFORE THE ARROW)
st.write("---")
# Creating a 4-column layout to house [Location | Image | Voice | Spacer]
c1, c2, c3, c4 = st.columns([0.15, 0.35, 0.45, 0.05])
with c1: loc_on = st.checkbox("📍", value=False)
with c2: img_on = st.file_uploader("📸", type=['png','jpg','jpeg'], label_visibility="collapsed")
with c3: voice_on = st.audio_input("🎙️", label_visibility="collapsed")

# THE MAIN BLUE INPUT
prompt = st.chat_input("Command, Sir...")

# --- [SECTION 5: LOGIC] ---
if voice_on:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        prompt = client.audio.transcriptions.create(model="whisper-1", file=io.BytesIO(voice_on.read())).text
    except: st.error("VOICE_FAIL")

if prompt:
    final_q = prompt + (" [LOC_ लाहौर, PK]" if loc_on else "")
    payload = [{"type": "text", "text": final_q}]
    if img_on:
        payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(img_on.read()).decode()}"}})
    
    st.session_state.messages.append({"role": "user", "content": payload})
    
    with st.chat_message("assistant"):
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
        stream = client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet", 
            messages=[{"role":"system","content":"You are OBITWICEX, a witty Lahori Yaar. Speak Roman Urdu, Punjabi, Finnish, Eng."}]+st.session_state.messages[-6:], 
            stream=True
        )
        full_reply = "".join([chunk.choices[0].delta.content for chunk in stream if chunk.choices[0].delta.content])
        st.markdown(full_reply)
        st.session_state.messages.append({"role": "assistant", "content": full_reply})
        speak(full_reply)
        st.rerun()
