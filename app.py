import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io, base64, requests

# --- [SECTION 1: SYSTEM CONFIGURATION] ---
st.set_page_config(
    page_title="OBITWICEX | ELITE_OS", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- [SECTION 2: HARDENED STEALTH CSS] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD & CLEAN TOP */
    .jarvis-hud-container { display: flex; justify-content: center; align-items: center; height: 160px; position: relative; width: 100%; margin-bottom: 5px; }
    .ring-1 { width: 130px; height: 130px; border: 2px solid #00E5FF; border-radius: 50%; border-top-color: transparent; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    
    .telemetry-bar { 
        font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; 
        letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 5px; 
        border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px; 
    }

    /* CHAT BUBBLES */
    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.04); border-left: 4px solid #00E5FF; 
        border-radius: 0px 10px 10px 0px; margin-bottom: 12px; 
    }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }

    /* KILL RED BORDER & ALIGN INPUT */
    .stChatInputContainer { 
        border: 1px solid #00E5FF !important; 
        border-radius: 20px !important; 
        background: #000 !important;
    }
    .stChatInputContainer:focus-within { 
        border-color: #00FF41 !important; 
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important; 
    }
    button[data-testid="stChatInputSubmit"] { fill: #00E5FF !important; }

    /* HIDE DEFAULTS */
    header, footer { visibility: hidden; }
    
    /* BLUE THEME FOR TACTICAL DOCK */
    .stCheckbox label span { color: #00E5FF !important; }
    </style>
    
    <div class="jarvis-hud-container"><div class="ring-1"></div></div>
    <div class="telemetry-bar">SYSTEM ENCRYPTION: <span style="color:#00FF41">DONE</span> &nbsp; | &nbsp; STATUS: <span style="color:#00FF41">UPLINK_OPTIMIZED</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: HARDENED ENGINES] ---
def speak_response(text):
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"].strip()
        url = f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        data = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
        res = requests.post(url, json=data, headers=headers)
        if res.status_code == 200:
            b64 = base64.b64encode(res.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def search_web(query):
    try:
        with DDGS() as ddgs:
            return " ".join([r.get('body', '') for r in ddgs.text(query, max_results=3)])
    except: return "SEARCH_OFFLINE"

# --- [SECTION 4: UI & STATE MANAGEMENT] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Render history
for m in st.session_state.messages:
    label = "USER_UPLINK" if m["role"] == "user" else "OBITWICEX_YAAR"
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{label}]</div>", unsafe_allow_html=True)
        text = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
        st.markdown(text)

# --- THE HORIZONTAL TACTICAL DOCK (WHATSAPP STYLE) ---
# We use st.columns right above the chat input to simulate the inline experience
st.write("---")
dock_col1, dock_col2, dock_col3 = st.columns([1, 1, 1])
with dock_col1: loc_share = st.checkbox("📍 SHARE LOC", value=False)
with dock_col2: screenshot = st.file_uploader("📸 SCAN IMAGE", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
with dock_col3: voice_data = st.audio_input("🎙️ VOICE MSG", label_visibility="collapsed")

prompt = st.chat_input("Command, Sir...")

# --- [SECTION 5: EXECUTION LOGIC] ---
if voice_data:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        audio_bytes = voice_data.read()
        audio_file = io.BytesIO(audio_bytes); audio_file.name = "v.wav"
        prompt = client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except: st.error("VOICE_DECRYPTION_FAILED")

if prompt:
    final_prompt = prompt + (" [LOCATION: Lahore, PK. Provide nearby context.]" if loc_share else "")
    user_payload = [{"type": "text", "text": final_prompt}]
    
    if screenshot:
        img_bytes = screenshot.read()
        b64_img = base64.b64encode(img_bytes).decode('utf-8')
        user_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}})
    
    st.session_state.messages.append({"role": "user", "content": user_payload})
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""
        sys_msg = "ROLE: OBITWICEX. Witty Lahori Yaar. Speak Roman Urdu, Punjabi, Finnish, Eng. Use SEARCH:[q] for location queries."
        
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
            stream = client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet", 
                messages=[{"role":"system","content":sys_msg}] + st.session_state.messages[-6:], 
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_YAAR]</div>\n\n{full_reply}", unsafe_allow_html=True)
            
            if "SEARCH:" in full_reply:
                q = full_reply.split("SEARCH:")[1].strip(" []")
                web_data = search_web(q)
                follow_up = client.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet",
                    messages=[{"role":"system","content":sys_msg}, {"role":"user","content":f"Results: {web_data}. Answer user: {prompt}"}]
                )
                full_reply = follow_up.choices[0].message.content
                placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_YAAR]</div>\n\n{full_reply}", unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": full_reply})
            speak_response(full_reply)
            st.rerun()
        except Exception as e:
            st.error(f"NEURAL_LINK_ERROR: Check Secrets API Key.")
