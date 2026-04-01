import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time

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

# --- 2. THE BRAIN (PAID LLAMA-3.3-70B) ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
    default_headers={
        "HTTP-Referer": "https://obitwicex.ai", 
        "X-Title": "Obitwicex Absolute Agent"
    }
)

# --- 3. MULTI-PROTOCOL RESEARCH ENGINE ---
def deep_research(query):
    try:
        with DDGS() as ddgs:
            q_low = query.lower()
            if any(k in q_low for k in ["9c", "cnsa", "narcotics", "law"]):
                search_q = f"{query} CNSA Narcotics Pakistan High Court Judgment 2026 site:pakistanlawsite.com OR site:lhc.gov.pk"
            elif any(k in q_low for k in ["ads", "seo", "marketing"]):
                search_q = f"{query} Google Ads policy SEO strategy Pakistan 2026"
            elif any(k in q_low for k in ["fbr", "secp", "tax"]):
                search_q = f"{query} FBR Income Tax Ordinance SECP Pakistan 2026"
            else:
                search_q = f"{query} Pakistan 2026 Business Law Technology"
                
            results = [r for r in ddgs.text(search_q, max_results=5)]
            return "\n\n".join([f"SYSTEM_ENTRY: {r['title']}\n{r['body']}" for r in results])
    except: 
        return "SYSTEM_LOG: Research bypass failed. Using core knowledge base."

# --- 4. SESSION ARCHITECTURE ---
if "messages" not in st.session_state: 
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_CORE")
    st.write("---")
    st.code("UPLINK: SECURE\nMODEL: LLAMA-3.3-ELITE\nSTATUS: NO_ERRORS", language="bash")
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
        
        # --- FIXED GREETING LOGIC ---
        if prompt.lower() in ["hi", "hello", "hey", "salam"]:
            full_response = "I am Obitwicex Your Everyday Ai Agent! I am Capable of guiding you through every Complex task! Anything You Want Try Me !"
        else:
            with st.status("INITIALIZING_CORE_REASONING...", expanded=True) as status:
                context = deep_research(prompt)
                sys_msg = f"""You are OBITWICEX ABSOLUTE AGENT. 
                - CRITICAL: No humor. Professional, high-level consultant tone.
                - LEGAL: 9-C is Narcotic Law (CNSA). FBR is Tax. Never confuse the two.
                - DOMAIN: Pakistan (LHC/SHC/FBR/SECP).
                - CONTEXT: {context}
                - LANGUAGE: Roman Urdu for advice, English for code/citations/legal references."""
                
                messages = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-8:]
                
                response = client.chat.completions.create(
                    model="meta-llama/llama-3.3-70b-instruct",
                    messages=messages,
                    stream=True
                )
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + " █")
                status.update(label="ANALYSIS_FINALIZED", state="complete")

        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
