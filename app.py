import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
from datetime import datetime
import io
import base64

# --- 1. ELITE PREMIUM HUD ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    .jarvis-hud-container {
        display: flex; justify-content: center; align-items: center;
        height: 200px; position: relative; width: 100%;
        background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 80%);
    }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 180px; height: 180px; border-top: 2px solid #00E5FF; animation: spin 8s linear infinite; }
    .ring-3 { width: 90px; height: 90px; background: #00E5FF; opacity: 0.2; border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes pulse { 0%, 100% { transform: scale(0.9); opacity: 0.1; } 50% { transform: scale(1.1); opacity: 0.4; } }

    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00E5FF;
        border-radius: 10px; margin-bottom: 15px;
    }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    
    <div class="jarvis-hud-container">
        <div class="ring ring-1"></div>
        <div class="ring ring-3"></div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. MULTI-AI BRAIN & DEVICE BRIDGE ---
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def agent_call(messages):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"].strip(),
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex Elite"}
        )
        return client.chat.completions.create(model="openrouter/auto", messages=messages, stream=True)
    except Exception as e:
        st.error(f"UPLINK_FAILURE: {str(e)}")
        return None

# --- 3. SYSTEM INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("### ⚡ DEVICE_UPLINK_PROTOCOLS")
col1, col2 = st.columns([1,1])
with col1:
    voice_data = st.audio_input("🎙️ VOICE_COMMAND")
with col2:
    screenshot = st.file_uploader("📸 VISUAL_SCAN", type=['png', 'jpg', 'jpeg'])

st.divider()

for m in st.session_state.messages:
    label = "[USER]" if m["role"] == "user" else "[OBITWICEX]"
    with st.chat_message(m["role"]):
        st.markdown(f"**{label}**\n\n{m['content']}")

# --- 4. EXECUTION ---
prompt = st.chat_input("Submit Command, Sir...")

if voice_data:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        audio_file = io.BytesIO(voice_data.read())
        audio_file.name = "voice.wav"
        prompt = client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except: st.error("VOICE_AUTH_FAIL")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**[USER]**\n\n{prompt}")

    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        full_reply = ""
        
        # Build Vision Content
        content = [{"type": "text", "text": prompt}]
        if screenshot:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot)}"}})

        sys_msg = """You are Obitwicex Omnipotent. Elite OS. 
        Always greet with 'Assalam o Alaikum, Sir'. Use Roman Urdu.
        If a user asks to perform a task on the device, output 'EXECUTE: [ACTION] | [TARGET]'.
        Example: 'EXECUTE: OPEN_APP | WhatsApp'."""
        
        msgs = [{"role": "system", "content": sys_msg}]
        for m in st.session_state.messages[-4:]:
            msgs.append({"role": m["role"], "content": m["content"]})
        msgs[-1]["content"] = content

        stream = agent_call(msgs)
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(f"**[OBITWICEX]**\n\n{full_reply} █")
            
            # DEVICE TASK TRIGGER
            if "EXECUTE:" in full_reply:
                st.toast(f"System Action Detected: {full_reply.split('EXECUTE:')[1]}")

            st.session_state.messages.append({"role": "assistant", "content": full_reply})
