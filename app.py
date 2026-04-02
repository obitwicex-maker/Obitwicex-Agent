import streamlit as st
from openai import OpenAI
import io, base64, requests

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CSS - KILLING ALL DEFAULTS] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD */
    .jarvis-hud { display: flex; justify-content: center; align-items: center; height: 120px; margin-top: -20px; }
    .ring-1 { width: 100px; height: 100px; border: 2px solid #00E5FF; border-radius: 50%; border-top-color: transparent; animation: spin 10s linear infinite; box-shadow: 0 0 10px #00E5FF; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    /* CHAT BUBBLES */
    div[data-testid="stChatMessage"] { background: rgba(0, 229, 255, 0.03); border-left: 3px solid #00E5FF; margin-bottom: 8px; }
    
    /* THE DOCK - NO RED BORDERS */
    .stTextInput input { background: #000 !important; color: #fff !important; border: 1px solid #00E5FF !important; }
    .stTextInput input:focus { border-color: #00FF41 !important; box-shadow: 0 0 10px #00FF41 !important; }
    
    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud"><div class="ring-1"></div></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: ENGINES] ---
def speak(text):
    try:
        api = st.secrets["ELEVENLABS_API_KEY"].strip()
        res = requests.post("https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM", 
            json={"text": text, "model_id": "eleven_multilingual_v2"}, 
            headers={"xi-api-key": api, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        if res.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(res.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- [SECTION 4: TACTICAL UPLINK DOCK] ---
if "messages" not in st.session_state: st.session_state.messages = []

# History Display
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m['content'][0]['text'] if isinstance(m['content'], list) else m['content'])

st.write("---")
# THE COMPACT WHATSAPP ROW
c1, c2, c3, c4, c5 = st.columns([0.1, 0.1, 0.1, 0.6, 0.1])
with c1: loc = st.checkbox("📍", label_visibility="collapsed")
with c2: img = st.file_uploader("📸", type=['jpg','png'], label_visibility="collapsed")
with c3: voice = st.audio_input("🎙️", label_visibility="collapsed")
with c4: cmd = st.text_input("", placeholder="Command, Sir...", label_visibility="collapsed")
with c5: push = st.button("🚀")

# --- [SECTION 5: EXECUTION] ---
if push and (cmd or voice):
    final_cmd = cmd
    if voice:
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
            final_cmd = client.audio.transcriptions.create(model="whisper-1", file=io.BytesIO(voice.read())).text
        except: st.error("VOICE_FAIL")
    
    if loc: final_cmd += " [User in Lahore, PK]"
    
    payload = [{"type": "text", "text": final_cmd}]
    if img: payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(img.read()).decode()}"}})
    
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
        except: st.error("CHECK OPENROUTER KEY IN SECRETS.")
