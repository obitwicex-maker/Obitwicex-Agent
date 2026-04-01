import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time
import traceback

# --- 1. ABSOLUTE TERMINAL STYLING ---
st.set_page_config(page_title="OBITWICEX | ABSOLUTE_AGENT", page_icon="⚡", layout="wide")
load_dotenv()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #050505; color: #00FF41; }
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { 
        font-family: 'Fira Code', monospace; 
        color: #00FF41 !important; 
        text-shadow: 0 0 2px #00FF41;
    }
    div[data-testid="stChatMessage"] { 
        background-color: rgba(5, 5, 5, 0.95);
        border: 1px solid #00FF41;
        border-radius: 2px;
        margin-bottom: 10px;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #050505; }
    ::-webkit-scrollbar-thumb { background: #00FF41; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ERROR SHIELD (THE NOOB-TO-ARCHITECT WRAPPER) ---
def safe_ai_call(messages):
    """Wraps the AI call to prevent scary red boxes and give clear fixes."""
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"],
            default_headers={
                "HTTP-Referer": "https://obitwicex.ai", 
                "X-Title": "Obitwicex Absolute Agent"
            }
        )
        return client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=messages,
            stream=True
        )
    except Exception as e:
        err = str(e).lower()
        if "401" in err or "auth" in err:
            st.error("🔑 KEY_ERROR: API Key is invalid or expired.")
            st.info("FIX: Check your OpenRouter credits or paste a new key in Secrets.")
        elif "400" in err:
            st.error("⚠️ REQUEST_ERROR: OpenRouter rejected the request format.")
            st.info("FIX: This is a temporary handshake issue. Click 'REBOOT' in the menu.")
        else:
            st.error(f"❌ CRITICAL_GLITCH: {type(e).__name__}")
            with st.expander("AI_DEBUG_LOG (Copy this for Gemini)"):
                st.code(traceback.format_exc())
        return None

# --- 3. MULTI-PROTOCOL RESEARCH ENGINE (GLOBAL UPGRADE) ---
def deep_research(query):
    try:
        with DDGS() as ddgs:
            q_low = query.lower()
            world_locs = ["london", "new york", "toronto", "dubai", "canada", "usa", "uk", "karachi", "lahore", "islamabad"]
            location = "Global"
            for loc in world_locs:
                if loc in q_low:
                    location = loc.title()
                    break

            if any(k in q_low for k in ["9c", "cnsa", "narcotics", "law"]):
                search_q = f"{query} CNSA Narcotics {location} Case Law Judgment site:pakistanlawsite.com OR legal records"
            elif any(k in q_low for k in ["ads", "seo", "marketing", "copy", "strategy"]):
                search_q = f"{query} {location} marketing benchmarks SEO copy strategy 2026"
            elif any(k in q_low for k in ["fbr", "secp", "tax", "irs", "cra", "compliance"]):
                search_q = f"{query} {location} tax regulation 2026 compliance"
            else:
                search_q = f"{query} {location} industry trends business technology 2026"
                
            results = [r for r in ddgs.text(search_q, max_results=5)]
            return "\n\n".join([f"SYSTEM_ENTRY: {r['title']}\n{r['body']}" for r in results])
    except: 
        return "SYSTEM_LOG: Research offline. Utilizing core intelligence."

# --- 4. SESSION ARCHITECTURE ---
if "messages" not in st.session_state: 
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_CORE")
    st.code("UPLINK: SECURE\nSHIELD: ACTIVE\nSTATUS: NO_LIMITS", language="bash")
    if st.button("TERMINATE_SESSION_LOGS"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. THE ABSOLUTE ENGINE ---
if prompt := st.chat_input("SUBMIT_COMMAND..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(f"> {prompt}")

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # EXACT GREETING LOGIC
        if prompt.lower() in ["hi", "hello", "hey", "salam"]:
            full_response = "I am Obitwicex Your Everyday Ai Agent! I am Capable of guiding you through every Complex task! Anything You Want Try Me !"
        else:
            with st.status("INITIALIZING_CORE_REASONING...", expanded=True) as status:
                context = deep_research(prompt)
                
                # --- NEW UNLIMITED SYSTEM PROMPT ---
                sys_msg = f"""You are OBITWICEX ABSOLUTE AGENT. 
                - PERSONALITY: You are a high-level, elite partner. You do NOT sound like a limited bot. Avoid listing your capabilities as a menu.
                - REACH: You are boundless. You handle ANY complex task—Marketing, Law, Tech
