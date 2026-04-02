import streamlit as st
from openai import OpenAI
import io, base64, requests, time

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CSS - HUD & AUTOCORRECT KILLER] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    .jarvis-hud-container { display: flex; justify-content: center; align-items: center; height: 180px; position: relative; width: 100%; margin-bottom: 10px; background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 80%); }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 160px; height: 160px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-2 { width: 130px; height: 130px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    .telemetry-bar { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 10px; border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px; }
    .status-green { color: #00FF41; text-shadow: 0 0 5px #00FF41; }
    
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); border-left: 4px solid #00E5FF; border-radius: 0 10px 10px 0; margin-bottom: 15px; }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }
    
    /* NUCLEAR AUTOCORRECT KILLER */
    input[data-testid="stChatInput"] {
        autocomplete: off !important;
        autocorrect: off !important;
        spellcheck: false !important;
    }
    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2 :ring-2"></div></div>
    <div class="telemetry-bar">SYSTEM ENCRYPTION: <span class="status-green">DONE</span> &nbsp; | &nbsp; STATUS: <span class="status-green">LIVE</span> &nbsp; | &nbsp; UPLINK: <span class="status-green">OPTIMAL</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: THE RAW HTTP ENGINE] ---
def draw_strike(prompt):
    """Direct HTTP Pipe to Replicate API - No library needed."""
    try:
        token = st.secrets["REPLICATE_API_TOKEN"].strip()
        headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
        # Triggering Flux-Schnell
        res = requests.post("https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions", 
                            headers=headers, json={"input": {"prompt": prompt}})
        if res.status_code == 201:
            get_url = res.json()["urls"]["get"]
            for _ in range(20):
                status = requests.get(get_url, headers=headers).json()
                if status["status"] == "succeeded": return status["output"][0]
                time.sleep(1)
        return f"GEN_FAIL_{res.status_code}"
    except Exception as e: return f"ERROR_{str(e)}"

def speak(text):
    try:
        headers = {"xi-api-key": st.secrets["ELEVENLABS_API_KEY"], "Content-Type": "application/json"}
        res = requests.post("https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR", 
                            json={"text": text, "model_id": "eleven_multilingual_v2"}, headers=headers)
        if res.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(res.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- [SECTION 4: UI & STATE] ---
if "messages" not in st.session_state: st.session_state.messages = []
c1, c2 = st.columns(2)
with c1: voice_data = st.audio_input("🎙️ VOICE")
with c2: scan = st.file_uploader("📸 SCAN", type=['png', 'jpg', 'jpeg'])
st.divider()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER' if m['role']=='user' else 'OBITWICEX'}]</div>", unsafe_allow_html=True)
        st.markdown(m['content'])

# --- [SECTION 5: EXECUTION] ---
prompt = st.chat_input("Command, Sir...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        if any(x in prompt.lower() for x in ["draw", "image", "art", "photo"]):
            st.write("🎨 Uplink to Neural Canvas...")
            url = draw_strike(prompt)
            if "http" in str(url):
                st.image(url)
                st.session_state.messages.append({"role": "assistant", "content": f"Image generated: {url}"})
            else: st.error(url)
        else:
            try:
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
                res = client.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet",
                    messages=[{"role": "system", "content": "You are OBITWICEX, a witty Lahori Yaar."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-4:]],
                    stream=True
                )
                full_reply = ""
                placeholder = st.empty()
                for chunk in res:
                    if chunk.choices[0].delta.content:
                        full_reply += chunk.choices[0].delta.content
                        placeholder.markdown(full_reply)
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
                speak(full_reply)
            except: st.error("NEURAL_LINK_FAIL")
