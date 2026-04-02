import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io, base64, requests

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CSS - THE RED LINE KILLER] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD */
    .jarvis-hud { display: flex; justify-content: center; align-items: center; height: 150px; margin-top: -20px; }
    .ring-1 { width: 120px; height: 120px; border: 2px solid #00E5FF; border-radius: 50%; border-top-color: transparent; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    .telemetry { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; background: rgba(0, 229, 255, 0.05); padding: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px; }

    /* CHAT BOXES */
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); border-left: 4px solid #00E5FF; border-radius: 0 10px 10px 0; margin-bottom: 10px; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; }

    /* CUSTOM INPUT BAR - NO RED BORDER */
    .stTextInput input {
        background-color: #000 !important;
        color: #FFFFFF !important;
        border: 1px solid #00E5FF !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus {
        border-color: #00FF41 !important;
        box-shadow: 0 0 10px #00FF41 !important;
    }

    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud"><div class="ring-1"></div></div>
    <div class="telemetry">SYSTEM ENCRYPTION: <span style="color:#00FF41">DONE</span> | STATUS: <span style="color:#00FF41">TACTICAL_UPLINK_ARMED</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE ENGINES] ---
def speak(text):
    try:
        res = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR", 
            json={"text": text, "model_id": "eleven_multilingual_v2"}, 
            headers={"xi-api-key": st.secrets["ELEVENLABS_API_KEY"].strip(), "Content-Type": "application/json", "Accept": "audio/mpeg"})
        if res.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(res.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- [SECTION 4: TACTICAL DOCK ARCHITECTURE] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Display Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER' if m['role']=='user' else 'OBITWICEX'}]</div>", unsafe_allow_html=True)
        st.markdown(m['content'][0]['text'] if isinstance(m['content'], list) else m['content'])

# THE DOCK - EVERYTHING IN ONE BLUE ROW AT THE BOTTOM
st.write("---")
c1, c2, c3, c4, c5 = st.columns([0.1, 0.1, 0.1, 0.6, 0.1])
with c1: loc_on = st.checkbox("📍", value=False, label_visibility="collapsed")
with c2: img_on = st.file_uploader("📸", type=['png','jpg','jpeg'], label_visibility="collapsed")
with c3: voice_on = st.audio_input("🎙️", label_visibility="collapsed")
with c4: prompt = st.text_input("", placeholder="Command, Sir...", label_visibility="collapsed")
with c5: send_btn = st.button("🚀")

# --- [SECTION 5: EXECUTION] ---
if send_btn and (prompt or voice_on):
    final_prompt = prompt
    if voice_on:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        final_prompt = client.audio.transcriptions.create(model="whisper-1", file=io.BytesIO(voice_on.read())).text
    
    if loc_on: final_prompt += " [Loc: Lahore, PK]"
    
    payload = [{"type": "text", "text": final_prompt}]
    if img_on: payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(img_on.read()).decode()}"}})
    
    st.session_state.messages.append({"role": "user", "content": payload})
    
    with st.chat_message("assistant"):
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
            stream = client.chat.completions.create(model="anthropic/claude-3.5-sonnet", messages=[{"role":"system","content":"You are OBITWICEX, a witty Lahori Yaar."}]+st.session_state.messages[-6:], stream=True)
            full_reply = "".join([chunk.choices[0].delta.content for chunk in stream if chunk.choices[0].delta.content])
            st.markdown(full_reply)
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
            speak(full_reply)
            st.rerun()
        except: st.error("NEURAL_LINK_ERROR: Check API Keys in Secrets.")
