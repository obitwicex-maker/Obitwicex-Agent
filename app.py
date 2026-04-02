import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from datetime import datetime

# --- 1. HUD & CENTER-CORE ANIMATION STYLING ---
st.set_page_config(page_title="OBITWICEX | AI_AGENT", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #050505; color: #00FF41; }
    
    .jarvis-orb-container {
        display: flex;
        justify-content: center;
        padding: 30px 0;
        width: 100%;
    }
    .jarvis-orb {
        width: 160px; height: 160px;
        background: radial-gradient(circle, #00FF41 0%, #001a07 70%);
        border-radius: 50%;
        box-shadow: 0 0 40px #00FF41, inset 0 0 40px #00FF41;
        animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
        0% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 20px #00FF41; }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 60px #00FF41; }
        100% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 20px #00FF41; }
    }

    div[data-testid="stChatMessage"] { 
        background: linear-gradient(180deg, rgba(0, 255, 65, 0.08) 0%, rgba(0, 5, 0, 1) 100%);
        border: 1px solid #00FF41;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    
    div[data-testid="stChatMessageAvatarUser"],
    div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    
    .stMarkdown p { font-family: 'Fira Code', monospace; color: #00FF41 !important; font-size: 1rem; }
    [data-testid="stSidebar"] { background-color: #050a05; border-right: 1px solid #1f3f1f; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE VOICE BRAIN (WHISPER) ---
def transcribe_voice(audio_file):
    try:
        key = st.secrets.get("OPENAI_API_KEY")
        if not key: return "SYSTEM_LOG: Missing OpenAI Key in Secrets."
        client = OpenAI(api_key=key)
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text
    except Exception as e:
        return f"VOICE_STREAMS_OFFLINE: {str(e)[:50]}"

# --- 3. THE CHAT BRAIN (OPENROUTER) ---
def agent_call(messages):
    try:
        or_key = st.secrets.get("OPENROUTER_API_KEY")
        if not or_key:
            st.error("SECRET_ERROR: OPENROUTER_API_KEY not found.")
            return None
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=or_key,
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex AI"}
        )
        # Using a backup model logic in case llama-3.3 is busy
        return client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=messages,
            stream=True
        )
    except Exception as e:
        st.error(f"UPLINK_FAILURE: {str(e)}")
        return None

# --- 4. THE INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_OS")
    st.markdown(f"**STATUS:** `ACTIVE`  \n**TIME:** `{datetime.now().strftime('%H:%M:%S')}`")
    st.divider()
    st.subheader("🎙️ Voice Command")
    voice_input = st.audio_input("Tap to record...")
    if voice_input:
        st.session_state.voice_text = transcribe_voice(voice_input)
    
    st.divider()
    if st.button("TERMINATE_SESSION"):
        st.session_state.messages = []
        st.rerun()

# MAIN SCREEN CENTER ORB
st.markdown('<div class="jarvis-orb-container"><div class="jarvis-orb"></div></div>', unsafe_allow_html=True)

# Render Chat
for message in st.session_state.messages:
    label = "USER_UPLINK" if message["role"] == "user" else "AGENT_RESPONSE"
    with st.chat_message(message["role"]):
        st.markdown(f"**[{label}]**\n\n{message['content']}")

# --- 5. LOGIC FLOW ---
prompt = st.chat_input("Enter command...")

if "voice_text" in st.session_state:
    prompt = st.session_state.voice_text
    del st.session_state.voice_text

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**[USER_UPLINK]**\n\n{prompt}")

    with st.chat_message("assistant"):
        response_ph = st.empty()
        full_res = ""
        
        # Ahmad Ali Kala Protocol
        if "ahmad ali kala" in prompt.lower():
            full_res = "Sir, analysis complete. Ahmad Ali Kala? Baat bazaar mein nahi rakhunga, dukan uski wahin kholunga jahan usne sochi bhi nahi hogi. Command me."
        else:
            sys_msg = "You are Obitwicex AI Agent. Professional, elite, and raw. Use Roman Urdu for chat, English for data."
            msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:]
            res = agent_call(msgs)
            
            if res:
                for chunk in res:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        response_ph.markdown(f"**[AGENT_RESPONSE]**\n\n{full_res} █")
            else:
                full_res = "CRITICAL_ERROR: Uplink fracture. Verify OpenRouter balance/key."

        response_ph.markdown(f"**[AGENT_RESPONSE]**\n\n{full_res}")
        st.session_state.messages.append({"role": "assistant", "content": full_res})
