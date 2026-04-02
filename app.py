import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
from datetime import datetime
import io
import base64
from PIL import Image

# --- 1. HUD & MULTIMODAL STYLING ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; }
    
    /* GLASS-NEON HUD */
    .jarvis-hud-container {
        display: flex; justify-content: center; align-items: center;
        height: 280px; position: relative; width: 100%;
        margin-bottom: 30px;
        background: radial-gradient(circle, rgba(0,229,255,0.08) 0%, transparent 75%);
    }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 240px; height: 240px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; }
    .ring-2 { width: 200px; height: 200px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    .ring-3 { 
        width: 120px; height: 120px; 
        background: radial-gradient(circle, #00E5FF 0%, transparent 80%);
        animation: breath 2.5s ease-in-out infinite;
    }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes breath { 0%, 100% { transform: scale(0.9); opacity: 0.4; } 50% { transform: scale(1.1); opacity: 0.9; } }

    /* PREMIUM CHAT BOXES */
    div[data-testid="stChatMessage"] { 
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 229, 255, 0.15);
        border-left: 5px solid #00E5FF;
        border-radius: 0px 15px 15px 0px;
        margin-bottom: 20px;
    }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .stMarkdown p { font-family: 'Fira Code', monospace; line-height: 1.6; }
    
    [data-testid="stSidebar"] { background-color: #000; border-right: 2px solid #00E5FF; }
    header {visibility: hidden;} footer {visibility: hidden;}

    /* CHAT INPUT BAR STYLING */
    .stChatInputContainer { border: 1px solid #00E5FF !important; background: #000 !important; }
    </style>
    
    <div class="jarvis-hud-container">
        <div class="ring ring-1"></div>
        <div class="ring ring-2"></div>
        <div class="ring ring-3"></div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. MULTIMODAL ENGINES ---
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r.get('body', '') for r in ddgs.text(query, max_results=3)]
            return " ".join(results)
    except: return "TASK_LINK_OFFLINE"

def transcribe_voice(audio_bytes):
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input.wav"
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        return client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except: return None

def agent_stream(messages):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"].strip(),
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex Elite"}
        )
        return client.chat.completions.create(
            model="meta-llama/llama-3.2-90b-vision-instruct", # VISION ENABLED MODEL
            messages=messages,
            stream=True 
        )
    except: return None

# --- 3. SYSTEM HUD SIDEBAR ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_ELITE_OS")
    st.markdown(f"**UPLINK:** `{datetime.now().strftime('%H:%M:%S')}`")
    st.markdown("**STATUS:** `ENCRYPTED LIVE` 🟢")
    st.divider()
    
    st.subheader("🎙️ Voice Protocol")
    voice_data = st.audio_input("Initiate Voice Link...")
    if voice_data:
        with st.spinner("🔍 DECODING_AUDIO..."):
            res = transcribe_voice(voice_data.read())
            if res: st.session_state.voice_text = res

    st.divider()
    st.subheader("📸 Visual Protocol")
    screenshot = st.file_uploader("Upload Screenshot for Analysis", type=['png', 'jpg', 'jpeg'])

# --- 4. HUD INTERFACE ---
for message in st.session_state.messages:
    label = "[USER_UPLINK]" if message["role"] == "user" else "[OBITWICEX_AGENT]"
    with st.chat_message(message["role"]):
        st.markdown(f"**{label}**\n\n{message['content']}")

# --- 5. EXECUTION LOGIC ---
prompt = st.chat_input("Submit Command, Sir...")

# Capture Voice or Upload
if "voice_text" in st.session_state:
    prompt = st.session_state.voice_text
    del st.session_state.voice_text

if prompt:
    user_content = [{"type": "text", "text": prompt}]
    
    # Check if a screenshot was shared
    if screenshot:
        base64_image = encode_image(screenshot)
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })
        st.info("🖼️ Screenshot attached to uplink.")

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(f"**[USER_UPLINK]**\n\n{prompt}")

    with st.chat_message("assistant"):
        resp_placeholder = st.empty()
        full_reply = ""
        sys_msg = "You are Obitwicex Elite OS. You have Vision and Browser access. Always greet with 'Assalam o Alaikum, Sir'. Respond in Roman Urdu. To search, say 'SEARCH: [query]'. Analyze screenshots with technical precision."
        
        # Prepare messages for vision-capable model
        msgs = [{"role": "system", "content": sys_msg}]
        for m in st.session_state.messages[-6:]:
            msgs.append({"role": m["role"], "content": m["content"]})
            
        # Update last message with screenshot if present
        if screenshot:
            msgs[-1]["content"] = user_content

        stream = agent_stream(msgs)
        if stream:
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply} █")
            
            if "SEARCH:" in full_reply:
                query = full_reply.split("SEARCH:")[1].strip(" []")
                with st.spinner(f"🌐 BROWSER_ACTIVE: Tasking {query}..."):
                    web_data = search_web(query)
                    msgs.append({"role": "assistant", "content": full_reply})
                    msgs.append({"role": "user", "content": f"Browser Data: {web_data}"})
                    new_stream = agent_stream(msgs)
                    full_reply = "" 
                    for chunk in new_stream:
                        if chunk.choices[0].delta.content:
                            full_reply += chunk.choices[0].delta.content
                            resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply} █")

            resp_placeholder.markdown(f"**[OBITWICEX_AGENT]**\n\n{full_reply}")
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
