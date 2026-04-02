import streamlit as st
from openai import OpenAI
import io, base64, requests, time

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: STEALTH HUD & CSS] ---
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
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); border-left: 4px solid #00E5FF; border-radius: 0 10px 10px 0; margin-bottom: 15px; }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }
    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div><div class="ring ring-3"></div></div>
    <div class="telemetry-bar">SYSTEM ENCRYPTION: DONE | STATUS CHECK: LIVE | UPLINK: REINFORCED</div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE ENGINES] ---
def speak(text):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR"
        headers = {"xi-api-key": st.secrets["ELEVENLABS_API_KEY"], "Content-Type": "application/json"}
        res = requests.post(url, json={"text": text, "model_id": "eleven_multilingual_v2"}, headers=headers)
        if res.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(res.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def gen_art(prompt):
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"].strip()
        res = requests.post(
            url="https://openrouter.ai/api/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"prompt": prompt, "model": "black-forest-labs/flux-schnell"} # Switched to Schnell for stability
        )
        if res.status_code == 200: return res.json()["data"][0]["url"]
        return f"ERROR_{res.status_code}"
    except: return "GEN_FAIL"

# --- [SECTION 4: UI & STATE] ---
if "messages" not in st.session_state: st.session_state.messages = []
c1, c2 = st.columns(2)
with c1: voice_data = st.audio_input("🎙️ VOICE INPUT")
with c2: screenshot = st.file_uploader("📸 SCAN IMAGE", type=['png', 'jpg', 'jpeg'])
st.divider()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER_UPLINK' if m['role']=='user' else 'OBITWICEX_YAAR'}]</div>", unsafe_allow_html=True)
        content = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
        st.markdown(content)

# --- [SECTION 5: EXECUTION] ---
prompt = st.chat_input("Command, Sir...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        low_p = prompt.lower()
        if any(x in low_p for x in ["draw", "image", "art", "photo"]):
            st.write("🎨 Uplink to Neural Canvas...")
            res = gen_art(prompt)
            if "ERROR" in str(res): st.error(res)
            else:
                st.image(res)
                st.session_state.messages.append({"role": "assistant", "content": f"Image: {res}"})
        else:
            try:
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
                # Clean history to prevent bad request errors
                clean_history = [{"role": m["role"], "content": (m["content"][0]["text"] if isinstance(m["content"], list) else m["content"])} for m in st.session_state.messages[-6:]]
                
                # Using the core identifier to bypass Amazon Bedrock routing errors
                stream = client.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet", 
                    messages=[{"role": "system", "content": "You are OBITWICEX, a witty Lahori Yaar."}] + clean_history, 
                    stream=True
                )
                full_reply = ""
                placeholder = st.empty()
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_reply += chunk.choices[0].delta.content
                        placeholder.markdown(full_reply)
                
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
                speak(full_reply)
            except Exception as e:
                # FALLBACK MODEL in case OpenRouter has a stroke
                st.warning("PRIMARY_LINK_LOST. SWITCHING TO BACKUP...")
                backup_res = client.chat.completions.create(
                    model="google/gemini-2.0-flash-001",
                    messages=[{"role": "user", "content": prompt}]
                )
                full_reply = backup_res.choices[0].message.content
                st.markdown(full_reply)
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
