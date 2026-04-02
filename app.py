import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time
from datetime import datetime

# --- 1. OBITWICEX TERMINAL STYLING ---
st.set_page_config(page_title="OBITWICEX | AI_AGENT", page_icon="🤖", layout="wide")
load_dotenv()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #050505; color: #00FF41; }
    div[data-testid="stChatMessage"] { 
        background: rgba(0, 255, 65, 0.03);
        border-left: 2px solid #00FF41;
        border-radius: 0px;
        margin-bottom: 10px;
    }
    .stMarkdown p { font-family: 'Fira Code', monospace; color: #00FF41 !important; }
    [data-testid="stSidebar"] { background-color: #0a130a; border-right: 1px solid #1f3f1f; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE ENGINES ---
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

with st.sidebar:
    st.title("🤖 OBITWICEX_AI")
    st.markdown("---")
    st.info("System: Online. Voice feature disabled until OpenAI Key is provided.")
    if st.button("TERMINATE SESSION"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. THE PRIMARY CHAT LOGIC ---
if prompt := st.chat_input("Type your command here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"> {prompt}")

    with st.chat_message("assistant"):
        response_ph = st.empty()
        full_res = ""
        prompt_low = prompt.lower()

        if "ahmad ali kala" in prompt_low:
            full_res = "Obitwicex Agent here. Ahmad Ali Kala? Baat bazaar mein nahi rakhunga, dukan uski wahin kholunga jahan usne sochi bhi nahi hogi."
        else:
            # NO NAMES USED HERE
            sys_msg = f"You are Obitwicex Ai Agent. Professional, raw, and highly intelligent. Current time {datetime.now().strftime('%H:%M')}. Use Roman Urdu for advice, English for technical data. Maintain elite status."
            
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
