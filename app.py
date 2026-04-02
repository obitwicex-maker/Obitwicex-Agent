import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time
import traceback
from datetime import datetime

# --- 1. OBITWICEX TERMINAL STYLING ---
st.set_page_config(page_title="OBITWICEX | AI_AGENT", page_icon="🤖", layout="wide")
load_dotenv()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #050505; color: #00FF41; }
    
    /* CHAT HUD */
    div[data-testid="stChatMessage"] { 
        background: rgba(0, 255, 65, 0.03);
        border-left: 2px solid #00FF41;
        border-radius: 0px;
        margin-bottom: 10px;
    }
    .stMarkdown p { font-family: 'Fira Code', monospace; color: #00FF41 !important; }
    
    /* SIDEBAR STYLING */
    [data-testid="stSidebar"] { background-color: #0a130a; border-right: 1px solid #1f3f1f; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE ENGINES (Transcribe & Brain) ---
def transcribe_voice(audio_file):
    try:
        client = OpenAI(api_key=st.secrets["OPENROUTER_API_KEY"]) # Using OpenAI for Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        return transcript.text
    except Exception as e:
        return f"Error transcribing: {str(e)}"

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
        st.error(f"UPLINK_FAILURE: {type(e).__name__}")
        return None

# --- 3. THE INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Optional Voice Feature in Sidebar
with st.sidebar:
    st.title("🤖 OBITWICEX_AI")
    st.markdown("---")
    st.subheader("🎙️ Voice Command (Optional)")
    voice_input = st.audio_input("Tap to speak...")
    
    if voice_input:
        with st.spinner("Processing voice..."):
            text_from_voice = transcribe_voice(voice_input)
            st.info(f"Transcribed: {text_from_voice}")
            # Injecting voice into chat logic
            st.session_state.voice_trigger = text_from_voice

    st.markdown("---")
    if st.button("TERMINATE SESSION"):
        st.session_state.messages = []
        st.rerun()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. THE PRIMARY CHAT LOGIC ---
prompt = st.chat_input("Type your command here...")

# If voice was used, override the prompt
if "voice_trigger" in st.session_state:
    prompt = st.session_state.voice_trigger
    del st.session_state.voice_trigger

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"> {prompt}")

    with st.chat_message("assistant"):
        response_ph = st.empty()
        full_res = ""
        prompt_low = prompt.lower()

        # Ahmad Ali Kala Logic
        if "ahmad ali kala" in prompt_low:
            full_res = "Obitwicex Agent here. Ahmad Ali Kala? Baat bazaar mein nahi rakhunga, dukan uski wahin kholunga jahan usne sochi bhi nahi hogi. Command confirmed."
        else:
            sys_msg = f"You are Obitwicex Ai Agent. Professional, raw, and highly intelligent. User is Obaid Butt. Current time {datetime.now().strftime('%H:%M')}. Use Roman Urdu for advice, English for technical data."
            
            msgs = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:]
            res = agent_call(msgs)
            
            if res:
                for chunk in res:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        response_ph.markdown(full_res + " █")
            else:
                full_res = "Connection fracture. Check system status."

        response_ph.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
