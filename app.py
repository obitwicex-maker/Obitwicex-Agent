import streamlit as st
from openai import OpenAI
import io, base64, requests, time

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
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div><div class="ring ring-3"></div></div>
    <div class="telemetry-bar">SYSTEM ENCRYPTION: <span class="status-green">DONE</span> | UPLINK: <span class="status-green">OPENROUTER_PRIMARY</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: OPENROUTER GENERATION ENGINE] ---
def gen_art_openrouter(prompt):
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"].strip()
        # Using OpenRouter's Image Generation Endpoint
        # Model: "stability-ai/stable-diffusion-xl" or "google/imagen-3"
        response = requests.post(
            url="https://openrouter.ai/api/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "prompt": prompt,
                "model": "stability-ai/sdxl", # High quality, widely available on OpenRouter
            }
        )
        if response.status_code == 200:
            return response.json()["data"][0]["url"]
        else:
            return f"ERROR_{response.status_code}: {response.text}"
    except Exception as e:
        return f"GEN_FAIL: {str(e)}"

def speak_response(text):
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR"
        headers = {"Accept": "audio/mpeg", "xi-api-key": api_key, "Content-Type": "application/json"}
        res = requests.post(url, json={"text": text, "model_id": "eleven_multilingual_v2"}, headers=headers)
        if res.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(res.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- [SECTION 4: UI & STATE MANAGEMENT] ---
if "messages" not in st.session_state: st.session_state.messages = []
col1, col2 = st.columns(2)
with col1: voice_data = st.audio_input("🎙️ VOICE INPUT")
with col2: screenshot = st.file_uploader("📸 SCAN IMAGE", type=['png', 'jpg', 'jpeg'])
st.divider()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m['content'][0]['text'] if isinstance(m['content'], list) else m['content'])

# --- [SECTION 5: EXECUTION LOGIC] ---
prompt = st.chat_input("Command, Sir...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        low_p = prompt.lower()
        if any(x in low_p for x in ["draw", "image", "art", "photo", "picture"]):
            st.write("🎨 **Routing through OpenRouter Neural Net...**")
            res = gen_art_openrouter(prompt)
            if "ERROR" in str(res):
                st.error(res)
                st.info("Sir, ensure your OpenRouter account has a few cents of credit for image generation.")
            else:
                st.image(res)
                st.session_state.messages.append({"role": "assistant", "content": f"Generated Image: {res}"})
        else:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
            stream = client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet", 
                messages=[{"role": "user", "content": prompt}], 
                stream=True
            )
            full_reply = "".join([c.choices[0].delta.content for c in stream if c.choices[0].delta.content])
            st.markdown(full_reply)
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
            speak_response(full_reply)
