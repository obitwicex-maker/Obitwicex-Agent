import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
from datetime import datetime
import io
import base64

# --- 1. PREMIUM GLASS HUD ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* ELITE HUD ANIMATION */
    .jarvis-hud-container {
        display: flex; justify-content: center; align-items: center;
        height: 220px; position: relative; width: 100%;
        background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 80%);
    }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 200px; height: 200px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; }
    .ring-3 { width: 100px; height: 100px; background: #00E5FF; opacity: 0.2; border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes pulse { 0% { transform: scale(0.8); opacity: 0.1; } 50% { transform: scale(1.1); opacity: 0.4; } 100% { transform: scale(0.8); opacity: 0.1; } }

    /* PREMIUM CHAT BOXES */
    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00E5FF;
        border-radius: 10px; margin-bottom: 15px;
    }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    
    /* HUD LABELS */
    .chat-label { font-family: 'Orbitron', sans-serif; font-weight: bold; color: #00E5FF; margin-bottom: 5px; font-size: 0.8rem; letter-spacing: 2px; }

    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    
    <div class="jarvis-hud-container">
        <div class="ring ring-1"></div>
        <div class="ring ring-3"></div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. THE MULTI-AI BRAIN ---
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def agent_call(messages):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"].strip(),
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex Elite"}
        )
        return client.chat.completions.create(
            # AUTO-ROUTER: Accesses GPT-4o, Claude 3.5, etc. dynamically
            model="openrouter/auto", 
            messages=messages,
            stream=True 
        )
    except Exception as e:
        st.error(f"UPLINK_ERROR: {str(e)}")
        return None

# --- 3. INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("### ⚡ OMNIPOTENT_PROTOCOLS")
col1, col2 = st.columns([1,1])
with col1:
    voice_data = st.audio_input("🎙️ VOICE_LINK")
with col2:
    screenshot = st.file_uploader("📸 VISUAL_DATA", type=['png', 'jpg', 'jpeg'])

st.divider()

# Display Chat History
for message in st.session_state.messages:
    label = "USER_COMMAND" if message["role"] == "user" else "OBITWICEX_RESPONSE"
    with st.chat_message(message["role"]):
        st.markdown(f"<div class='chat-label'>[{label}]</div>", unsafe_allow_html=True)
        st.markdown(message['content'])

# --- 4. EXECUTION ---
prompt = st.chat_input("Submit Command, Sir...")

# Handle Voice via OpenAI Whisper
if voice_data:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        audio_file = io.BytesIO(voice_data.read())
        audio_file.name = "voice.wav"
        prompt = client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except: st.error("VOICE_STREAM_AUTH_FAIL")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown("<div class='chat-label'>[USER_COMMAND]</div>", unsafe_allow_html=True)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        full_reply = ""
        
        # Multimodal Content Assembly
        content = [{"type": "text", "text": prompt}]
        if screenshot:
            base64_img = encode_image(screenshot)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
            })

        sys_msg = "You are the Obitwicex Omnipotent Agent. You utilize the world's best AI models via OpenRouter. Always greet with 'Assalam o Alaikum, Sir'. Speak in Roman Urdu. Be precise, efficient, and proactive. You can analyze images and search the web."
        
        msgs = [{"role": "system", "content": sys_msg}]
        # History for context
        for m in st.session_state.messages[-6:]:
            msgs.append({"role": m["role"], "content": m["content"]})
        
        # Attach current multimodal context
        msgs[-1]["content"] = content

        stream = agent_call(msgs)
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_RESPONSE]</div>\n\n{full_reply} █", unsafe_allow_html=True)
            
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
