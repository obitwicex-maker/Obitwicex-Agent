import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
from datetime import datetime
import io
import base64

# --- 1. PREMIUM GLASS HUD & TERMINAL STYLE ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* TRIPLE-RING JARVIS HUD */
    .jarvis-hud-container {
        display: flex; justify-content: center; align-items: center;
        height: 250px; position: relative; width: 100%;
        background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 80%);
        margin-bottom: 20px;
    }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { 
        width: 220px; height: 220px; border-top: 2px solid #00E5FF; 
        animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF;
    }
    .ring-2 { 
        width: 180px; height: 180px; border-right: 2px solid #00838F; 
        animation: spin 5s linear infinite reverse; 
    }
    .ring-3 { 
        width: 100px; height: 100px; background: #00E5FF; 
        opacity: 0.2; border-radius: 50%; animation: pulse 2s infinite; 
    }
    
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes pulse { 0%, 100% { transform: scale(0.8); opacity: 0.1; } 50% { transform: scale(1.1); opacity: 0.4; } }

    /* CHAT HUD BOXES */
    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.1);
        border-left: 4px solid #00E5FF;
        border-radius: 0px 10px 10px 0px;
        margin-bottom: 15px;
    }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    
    /* HUD LABELS */
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }

    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    
    <div class="jarvis-hud-container">
        <div class="ring ring-1"></div>
        <div class="ring ring-2"></div>
        <div class="ring ring-3"></div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. CORE ENGINES (Vision, Browser, Auto-AI) ---
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r.get('body', '') for r in ddgs.text(query, max_results=3)]
            return " ".join(results)
    except: return "DATA_UPLINK_OFFLINE"

def agent_call(messages):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"].strip(),
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex Elite"}
        )
        return client.chat.completions.create(
            model="openrouter/auto", # DYNAMIC BEST-MODEL SELECTION
            messages=messages,
            stream=True 
        )
    except Exception as e:
        st.error(f"UPLINK_ERROR: {str(e)}")
        return None

# --- 3. SYSTEM INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("### ⚡ OMNIPOTENT_PROTOCOLS")
col1, col2 = st.columns([1,1])
with col1:
    voice_data = st.audio_input("🎙️ VOICE_COMMAND")
with col2:
    screenshot = st.file_uploader("📸 VISUAL_SCAN", type=['png', 'jpg', 'jpeg'])

st.divider()

for m in st.session_state.messages:
    label = "USER_UPLINK" if m["role"] == "user" else "OBITWICEX_RESPONSE"
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{label}]</div>", unsafe_allow_html=True)
        st.markdown(m['content'])

# --- 4. EXECUTION FLOW ---
prompt = st.chat_input("Submit Command, Sir...")

# Handle Voice via OpenAI Whisper
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
        st.markdown("<div class='chat-label'>[USER_UPLINK]</div>", unsafe_allow_html=True)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        full_reply = ""
        
        # Build Multimodal Packet
        content = [{"type": "text", "text": prompt}]
        if screenshot:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot)}"}})

        sys_msg = """You are Obitwicex Omnipotent. Elite AI OS. 
        1. Always greet with 'Assalam o Alaikum, Sir' or 'Salam, Sir'. 
        2. Use Roman Urdu for chat. Use English for technical data.
        3. If tasked with device control, output: 'EXECUTE: [ACTION] | [TARGET]'.
        4. Use the web via SEARCH: [query] if needed."""
        
        msgs = [{"role": "system", "content": sys_msg}]
        for m in st.session_state.messages[-4:]:
            msgs.append({"role": m["role"], "content": m["content"]})
        msgs[-1]["content"] = content

        stream = agent_call(msgs)
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_RESPONSE]</div>\n\n{full_reply} █", unsafe_allow_html=True)
            
            # Browser task logic
            if "SEARCH:" in full_reply:
                query = full_reply.split("SEARCH:")[1].strip(" []")
                with st.spinner(f"🌐 BROWSER_LINK_ACTIVE: Searching {query}..."):
                    web_data = search_web(query)
                    msgs.append({"role": "assistant", "content": full_reply})
                    msgs.append({"role": "user", "content": f"Results: {web_data}"})
                    new_stream = agent_call(msgs)
                    full_reply = "" 
                    for chunk in new_stream:
                        if chunk.choices[0].delta.content:
                            full_reply += chunk.choices[0].delta.content
                            resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_RESPONSE]</div>\n\n{full_reply} █", unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": full_reply})
