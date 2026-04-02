import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time
from datetime import datetime

# --- 1. JARVIS HUD & ANIMATION STYLING (THE COOL VIBE) ---
st.set_page_config(page_title="OBITWICEX | AI_AGENT", page_icon="⚡", layout="wide")
load_dotenv()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    
    .stApp { background-color: #050505; color: #00FF41; }
    
    /* THE JARVIS ORB ANIMATION */
    .jarvis-orb {
        width: 120px; height: 120px;
        background: radial-gradient(circle, #00FF41 0%, #001a07 70%);
        border-radius: 50%;
        margin: 20px auto;
        box-shadow: 0 0 20px #00FF41, inset 0 0 20px #00FF41;
        animation: pulse 2s infinite ease-in-out;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 10px #00FF41; }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 40px #00FF41; }
        100% { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 10px #00FF41; }
    }

    /* HUD CHAT STYLING */
    div[data-testid="stChatMessage"] { 
        background: rgba(0, 255, 65, 0.05);
        border: 1px solid rgba(0, 255, 65, 0.2);
        border-radius: 5px;
        margin-bottom: 10px;
        font-family: 'Fira Code', monospace;
    }
    
    .stMarkdown p { color: #00FF41 !important; text-shadow: 0 0 5px rgba(0,255,65,0.3); }
    [data-testid="stSidebar"] { background-color: #050a05; border-right: 1px solid #1f3f1f; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE BRAIN ---
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
    except Exception as e:
        return None

# --- 3. THE HUD INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown('<div class="jarvis-orb"></div>', unsafe_allow_html=True)
    st.title("⚡ OBITWICEX_OS")
    st.markdown(f"**STATUS:** `SECURE`  \n**UPLINK:** `ACTIVE`  \n**LOCAL_TIME:** `{datetime.now().strftime('%H:%M:%S')}`")
    st.divider()
    
    # Talk option added back as requested (Optional)
    st.subheader("🎙️ Voice Protocol")
    st.audio_input("Tap to record (Audio only)")
    st.caption("Voice transcription requires OpenAI Key.")
    
    if st.button("TERMINATE_LOGS"):
        st.session_state.messages = []
        st.rerun()

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. COMMAND LOGIC ---
if prompt := st.chat_input("SUBMIT_COMMAND..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"USER_UPLINK: {prompt}")

    with st.chat_message("assistant"):
        response_ph = st.empty()
        full_res = ""
        prompt_low = prompt.lower()

        if "ahmad ali kala" in prompt_low:
            full_res = "Sir, analysis complete. Ahmad Ali Kala? Baat bazaar mein nahi rakhunga, dukan uski wahin kholunga jahan usne sochi bhi nahi hogi."
        else:
            sys_msg = f"You are Obitwicex AI Agent. You are an elite, raw, and authentic partner. Understand local Punjabi/Urdu slang. Current time {datetime.now().strftime('%H:%M')}. Speak Roman Urdu for advice, English for data. Match user energy."
            
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
