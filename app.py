import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io, base64, requests
from datetime import datetime

# --- [SECTION 1: SYSTEM CONFIGURATION] ---
st.set_page_config(
    page_title="OBITWICEX | ELITE_OS", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- [SECTION 2: STEALTH HUD & TELEMETRY] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    .jarvis-hud-container {
        display: flex; justify-content: center; align-items: center;
        height: 200px; position: relative; width: 100%;
        background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 80%);
        margin-bottom: 10px;
    }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 180px; height: 180px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-2 { width: 150px; height: 150px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    .ring-3 { width: 80px; height: 80px; background: #00E5FF; opacity: 0.2; border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes pulse { 0%, 100% { transform: scale(0.8); opacity: 0.1; } 50% { transform: scale(1.1); opacity: 0.4; } }
    .telemetry-bar {
        font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center;
        letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 5px;
        border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px;
    }
    .status-green { color: #00FF41; text-shadow: 0 0 5px #00FF41; }
    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.1); border-left: 4px solid #00E5FF;
        border-radius: 0px 10px 10px 0px; margin-bottom: 15px;
    }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div><div class="ring ring-3"></div></div>
    <div class="telemetry-bar">SYSTEM ENCRYPTION: <span class="status-green">DONE</span> &nbsp; | &nbsp; STATUS CHECK: <span class="status-green">LIVE</span> &nbsp; | &nbsp; UPLINK: <span class="status-green">OPTIMAL</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE & GENERATION ENGINES] ---
def gen_art(prompt):
    try:
        # RAW API CALL to bypass library version conflicts
        api_token = st.secrets["REPLICATE_API_TOKEN"].strip()
        # Flux-Schnell via Replicate API
        model_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
        headers = {"Authorization": f"Token {api_token}", "Content-Type": "application/json"}
        response = requests.post(model_url, headers=headers, json={"input": {"prompt": prompt}})
        
        if response.status_code == 201:
            prediction = response.json()
            poll_url = prediction["urls"]["get"]
            # Polling for result
            while True:
                poll_res = requests.get(poll_url, headers=headers).json()
                if poll_res["status"] == "succeeded": return poll_res["output"][0]
                if poll_res["status"] == "failed": return "ERROR: Generation Failed."
        return f"ERROR: API_REJECTED_{response.status_code}"
    except Exception as e: return f"GEN_FAIL: {str(e)}"

def speak_response(text):
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR"
        headers = {"Accept": "audio/mpeg", "xi-api-key": api_key, "Content-Type": "application/json"}
        response = requests.post(url, json={"text": text, "model_id": "eleven_multilingual_v2"}, headers=headers)
        if response.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(response.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- [SECTION 4: UI & STATE MANAGEMENT] ---
if "messages" not in st.session_state: st.session_state.messages = []
col1, col2 = st.columns(2)
with col1: voice_data = st.audio_input("🎙️ VOICE INPUT")
with col2: screenshot = st.file_uploader("📸 SCAN IMAGE", type=['png', 'jpg', 'jpeg'])
st.divider()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER_UPLINK' if m['role']=='user' else 'OBITWICEX_YAAR'}]</div>", unsafe_allow_html=True)
        text = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
        st.markdown(text)

# --- [SECTION 5: EXECUTION LOGIC] ---
prompt = st.chat_input("Command, Sir...")

if voice_data:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        prompt = client.audio.transcriptions.create(model="whisper-1", file=io.BytesIO(voice_data.read())).text
    except: st.error("VOICE_FAIL")

if prompt:
    user_payload = [{"type": "text", "text": prompt}]
    if screenshot:
        user_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot)}"}})
    st.session_state.messages.append({"role": "user", "content": user_payload})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        low_p = prompt.lower()
        if any(x in low_p for x in ["draw", "image", "generate picture", "photo", "art"]):
            st.write("🎨 **Uplink to Flux-Schnell... Processing Neural Layer...**")
            res = gen_art(prompt)
            if "ERROR" in str(res): st.error(res)
            else:
                st.image(res)
                st.session_state.messages.append({"role": "assistant", "content": f"Image generated: {res}"})
        else:
            resp_placeholder = st.empty(); full_reply = ""
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
            stream = client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet", 
                messages=[{"role": "system", "content": "You are OBITWICEX, a witty Lahori Yaar."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]], 
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(full_reply)
            if full_reply:
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
                speak_response(full_reply)
