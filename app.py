import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io
import base64
import requests
from datetime import datetime

# --- [SECTION 1: SYSTEM CONFIGURATION] ---
st.set_page_config(
    page_title="OBITWICEX | ELITE_OS", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- [SECTION 2: PREMIUM HUD & VISUAL ENGINE] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    
    /* BASE THEME */
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* JARVIS TRIPLE-RING HUD ANIMATION */
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

    /* CHAT BOX STYLING */
    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.1);
        border-left: 4px solid #00E5FF;
        border-radius: 0px 10px 10px 0px;
        margin-bottom: 15px;
    }
    
    /* CLEANUP */
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    
    <div class="jarvis-hud-container">
        <div class="ring ring-1"></div>
        <div class="ring ring-2"></div>
        <div class="ring ring-3"></div>
    </div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE FUNCTIONAL ENGINES] ---

def speak_response(text):
    """ElevenLabs TTS Integration for Jarvis Voice"""
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"]
        voice_id = "pNInz6obpgnuM0s4qhGR" # George/Jarvis Style
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {"Accept": "audio/mpeg", "xi-api-key": api_key, "Content-Type": "application/json"}
        data = {
            "text": text, 
            "model_id": "eleven_multilingual_v2", 
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

def encode_image(image_file):
    """Convert uploaded images to Base64 for AI Vision"""
    return base64.b64encode(image_file.read()).decode('utf-8')

def search_web(query):
    """DuckDuckGo Real-Time Web Access"""
    try:
        with DDGS() as ddgs:
            results = [r.get('body', '') for r in ddgs.text(query, max_results=3)]
            return " ".join(results)
    except:
        return "DATA_UPLINK_OFFLINE"

def agent_call(messages):
    """Multi-Model Failover Brain (Claude -> GPT -> Llama)"""
    models = ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "meta-llama/llama-3.3-70b-instruct"]
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1", 
        api_key=st.secrets["OPENROUTER_API_KEY"].strip()
    )
    for model_id in models:
        try:
            return client.chat.completions.create(model=model_id, messages=messages, stream=True)
        except:
            continue 
    return None

# --- [SECTION 4: UI & STATE MANAGEMENT] ---

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("### ⚡ OMNIPOTENT_PROTOCOLS")
col1, col2 = st.columns(2)
with col1:
    voice_data = st.audio_input("🎙️ VOICE_LINK")
with col2:
    screenshot = st.file_uploader("📸 VISUAL_SCAN", type=['png', 'jpg', 'jpeg'])

st.divider()

# RENDER CHAT HISTORY
for m in st.session_state.messages:
    label = "USER_UPLINK" if m["role"] == "user" else "OBITWICEX_YAAR"
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{label}]</div>", unsafe_allow_html=True)
        text = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
        st.markdown(text)

# --- [SECTION 5: EXECUTION LOGIC] ---

prompt = st.chat_input("Submit Command, Sir...")

# HANDLE VOICE (Whisper)
if voice_data:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        audio_file = io.BytesIO(voice_data.read())
        audio_file.name = "v.wav"
        prompt = client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except:
        st.error("VOICE_AUTH_FAIL")

if prompt:
    # 1. LOG USER INPUT
    user_payload = [{"type": "text", "text": prompt}]
    if screenshot:
        user_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot)}"}})
    
    st.session_state.messages.append({"role": "user", "content": user_payload})
    with st.chat_message("user"):
        st.markdown("<div class='chat-label'>[USER_UPLINK]</div>", unsafe_allow_html=True)
        st.markdown(prompt)

    # 2. GENERATE AI RESPONSE
    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        full_reply = ""
        
        # FRIENDSHIP & LANGUAGE PROTOCOL
        sys_msg = """
        ROLE: OBITWICEX_JARVIS / BEST YAAR. GREET: 'Assalam o Alaikum, Sir'. 
        - Detect Lang (Roman Urdu/Eng) and match energy. 
        - Informal, sharp, witty. No filters for slangs or rough talk. 
        - Match trolls with trolls. 
        - USE SEARCH: [q] or EXECUTE: [a]|[t] ONLY when needed.
        """
        
        msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-6:]
        stream = agent_call(msgs)
        
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_YAAR]</div>\n\n{full_reply} █", unsafe_allow_html=True)
            
            # WEB SEARCH HOOK
            if "SEARCH:" in full_reply:
                q = full_reply.split("SEARCH:")[1].strip(" []")
                web_data = search_web(q)
                msgs.append({"role": "assistant", "content": full_reply})
                msgs.append({"role": "user", "content": f"Results: {web_data}"})
                new_stream = agent_call(msgs)
                full_reply = "" 
                for chunk in new_stream:
                    if chunk.choices[0].delta.content:
                        full_reply += chunk.choices[0].delta.content
                        resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_YAAR]</div>\n\n{full_reply} █", unsafe_allow_html=True)
            
            # 3. TRIGGER SPEECH OUTPUT
            speak_response(full_reply)
            
            # 4. SAVE FINAL RESPONSE
            st.session_state.messages.append({"role": "assistant", "content": full_reply})

# --- [END OF CODE] ---
