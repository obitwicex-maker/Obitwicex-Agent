import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import io
import base64

# --- 1. ELITE PREMIUM HUD & GLASSMORPHISM ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    .jarvis-hud-container {
        display: flex; justify-content: center; align-items: center;
        height: 220px; position: relative; width: 100%;
        background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 80%);
        margin-bottom: 20px;
    }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 210px; height: 210px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-3 { width: 100px; height: 100px; background: #00E5FF; opacity: 0.2; border-radius: 50%; animation: pulse 2s infinite; }
    
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes pulse { 0%, 100% { transform: scale(0.9); opacity: 0.1; } 50% { transform: scale(1.1); opacity: 0.4; } }

    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 229, 255, 0.1); border-left: 5px solid #00E5FF;
        border-radius: 10px; margin-bottom: 15px;
    }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    
    <div class="jarvis-hud-container">
        <div class="ring ring-1"></div>
        <div class="ring ring-3"></div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. THE UNSTOPPABLE FAILOVER ENGINE ---
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def search_web(query):
    try:
        with DDGS() as ddgs:
            return " ".join([r.get('body', '') for r in ddgs.text(query, max_results=3)])
    except: return "DATA_UPLINK_OFFLINE"

def agent_call(messages):
    # REDUNDANT BRAIN STACK
    models = ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "meta-llama/llama-3.3-70b-instruct"]
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())

    for model_id in models:
        try:
            return client.chat.completions.create(model=model_id, messages=messages, stream=True)
        except: continue # Auto-switches brain if provider fails
    return None

# --- 3. SYSTEM INTERFACE ---
if "messages" not in st.session_state: st.session_state.messages = []
st.markdown("### ⚡ OMNIPOTENT_PROTOCOLS")
col1, col2 = st.columns(2)
with col1: voice_data = st.audio_input("🎙️ VOICE_LINK")
with col2: screenshot = st.file_uploader("📸 VISUAL_SCAN", type=['png', 'jpg', 'jpeg'])
st.divider()

for m in st.session_state.messages:
    label = "USER_UPLINK" if m["role"] == "user" else "OBITWICEX_RESPONSE"
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{label}]</div>", unsafe_allow_html=True)
        text = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
        st.markdown(text)

# --- 4. EXECUTION FLOW ---
prompt = st.chat_input("Submit Command, Sir...")
if voice_data:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        audio_file = io.BytesIO(voice_data.read()); audio_file.name = "v.wav"
        prompt = client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except: st.error("VOICE_AUTH_FAIL")

if prompt:
    user_payload = [{"type": "text", "text": prompt}]
    if screenshot:
        user_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(screenshot)}"}})
    st.session_state.messages.append({"role": "user", "content": user_payload})
    
    with st.chat_message("user"):
        st.markdown("<div class='chat-label'>[USER_UPLINK]</div>", unsafe_allow_html=True)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        resp_placeholder = st.empty(); full_reply = ""
        sys_msg = """ROLE: OBITWICEX_JARVIS. 
        1. GREET: 'Assalam o Alaikum, Sir'. 
        2. LANG: Match user (Roman Urdu or English). 
        3. VIBE: Brief, elite, professional. 
        4. CMD: SEARCH: [q] or EXECUTE: [a]|[t]. 
        5. NEVER explain yourself."""
        
        msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-6:]
        stream = agent_call(msgs)
        
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_RESPONSE]</div>\n\n{full_reply} █", unsafe_allow_html=True)
            
            if "SEARCH:" in full_reply:
                q = full_reply.split("SEARCH:")[1].strip(" []")
                web_data = search_web(q)
                msgs.append({"role": "assistant", "content": full_reply})
                msgs.append({"role": "user", "content": f"Results: {web_data}"})
                new_stream = agent_call(msgs); full_reply = "" 
                for chunk in new_stream:
                    if chunk.choices[0].delta.content:
                        full_reply += chunk.choices[0].delta.content
                        resp_placeholder.markdown(f"<div class='chat-label'>[OBITWICEX_RESPONSE]</div>\n\n{full_reply} █", unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": full_reply})
