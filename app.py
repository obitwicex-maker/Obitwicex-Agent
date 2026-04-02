import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time
from datetime import datetime

# --- 1. HUD & ANIMATION STYLING (MOBILE OPTIMIZED) ---
st.set_page_config(page_title="OBITWICEX | AI_AGENT", page_icon="⚡", layout="wide")
load_dotenv()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #050505; color: #00FF41; }
    
    /* THE JARVIS ORB */
    .jarvis-orb {
        width: 100px; height: 100px;
        background: radial-gradient(circle, #00FF41 0%, #001a07 70%);
        border-radius: 50%;
        margin: 10px auto;
        box-shadow: 0 0 20px #00FF41, inset 0 0 20px #00FF41;
        animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
        0% { transform: scale(0.85); opacity: 0.7; }
        50% { transform: scale(1.0); opacity: 1; box-shadow: 0 0 35px #00FF41; }
        100% { transform: scale(0.85); opacity: 0.7; }
    }

    /* MOBILE VISIBILITY: Show orb on main screen only on small devices */
    @media (min-width: 768px) {
        .mobile-only-orb { display: none; }
    }

    div[data-testid="stChatMessage"] { 
        background: linear-gradient(180deg, rgba(0, 255, 65, 0.08) 0%, rgba(0, 5, 0, 1) 100%);
        border: 1px solid #00FF41;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stMarkdown p { font-family: 'Fira Code', monospace; color: #00FF41 !important; }
    [data-testid="stSidebar"] { background-color: #050a05; border-right: 1px solid #1f3f1f; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE ENGINES ---
def transcribe_voice(audio_file):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text
    except Exception as e:
        return f"VOICE_ERROR: {str(e)}"

def agent_call(messages):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"],
            default_headers={"HTTP-Referer": "https://obitwicex.ai", "X-Title": "Obitwicex Agent"}
        )
        return client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=messages,
            stream=True
        )
    except: return None

# --- 3. THE HUD INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- NEW: MOBILE RESPONSIVE ORB ---
# This div will show up at the top of the chat ONLY on mobile
st.markdown('<div class="mobile-only-orb"><div class="jarvis-orb"></div></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="jarvis-orb"></div>', unsafe_allow_html=True)
    st.title("⚡ OBITWICEX_OS")
    st.markdown(f"**UPLINK:** `SECURE`  \n**TIME:** `{datetime.now().strftime('%H:%M:%S')}`")
    st.divider()
    
    st.subheader("🎙️ Voice Protocol")
    voice_input = st.audio_input("Tap to speak...")
    
    if voice_input:
        with st.spinner("TRANSCRIBING..."):
            st.session_state.voice_text = transcribe_voice(voice_input)

    if st.button("TERMINATE_LOGS"):
        st.session_state.messages = []
        st.rerun()

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. COMMAND LOGIC ---
prompt = st.chat_input("SUBMIT_COMMAND...")
if "voice_text" in st.session_state:
    prompt = st.session_state.voice_text
    del st.session_state.voice_text

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"USER_UPLINK: {prompt}")

    with st.chat_message("assistant"):
        response_ph = st.empty()
        full_res = ""
        prompt_low = prompt.lower()

        if "ahmad ali kala" in prompt_low:
            full_res = "Analysis complete. Ahmad Ali Kala? Baat bazaar mein nahi rakhunga, dukan uski wahin kholunga jahan usne sochi bhi nahi hogi."
        else:
            sys_msg = "You are Obitwicex AI Agent. Elite partner. Use Roman Urdu for advice, English for data. Match user energy."
            msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:]
            res = agent_call(msgs)
            
            if res:
                for chunk in res:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        response_ph.markdown(full_res + " █")
            else:
                full_res = "Uplink fracture detected."

        response_ph.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
