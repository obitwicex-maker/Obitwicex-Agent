import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time

# --- 1. HACKER TERMINAL STYLING (THE "ELITE" LOOK) ---
st.set_page_config(page_title="OBITWICEX | ELITE_AGENT", page_icon="⚡", layout="wide")
load_dotenv()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    
    .stApp { 
        background-color: #050505; 
        background-image: linear-gradient(0deg, transparent 24%, rgba(32, 255, 77, .05) 25%, rgba(32, 255, 77, .05) 26%, transparent 27%, transparent 74%, rgba(32, 255, 77, .05) 75%, rgba(32, 255, 77, .05) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(32, 255, 77, .05) 25%, rgba(32, 255, 77, .05) 26%, transparent 27%, transparent 74%, rgba(32, 255, 77, .05) 75%, rgba(32, 255, 77, .05) 76%, transparent 77%, transparent);
        background-size: 50px 50px;
    }
    
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { 
        font-family: 'Fira Code', monospace; 
        color: #00FF41 !important; 
        text-shadow: 0 0 5px #00FF41;
    }

    div[data-testid="stChatMessage"] { 
        background-color: rgba(10, 10, 10, 0.9) !important;
        border: 1px solid #00FF41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
        border-radius: 4px !important;
    }

    /* THE SCANLINE EFFECT */
    .stApp::before {
        content: " ";
        display: block;
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        z-index: 2;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE BRAIN (CRITICAL BYPASS HEADERS) ---
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets["OPENROUTER_API_KEY"],
        default_headers={
            "HTTP-Referer": "https://obitwicex.ai", 
            "X-Title": "Obitwicex Elite Terminal"
        }
    )
except Exception as e:
    st.error(f"SYSTEM_FAILURE: {e}")

# --- 3. SEARCH ENGINE ---
def deep_research(query):
    try:
        with DDGS() as ddgs:
            pak_query = f"{query} site:sindhhighcourt.gov.pk OR site:lhc.gov.pk OR site:fbr.gov.pk"
            results = [r for r in ddgs.text(pak_query, max_results=4)]
            return "\n\n".join([f"DATA_LINK: {r['title']}\n{r['body']}" for r in results])
    except: 
        return "LOCAL_DB_ENCRYPTED_ACCESS_ONLY"

if "messages" not in st.session_state: 
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_CTRL")
    st.write("---")
    st.code("STATUS: ENCRYPTED\nUPLINK: ACTIVE\nCREDITS: VERIFIED", language="bash")
    if st.button("PURGE_ALL_DATA"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. THE REASONING ENGINE ---
if prompt := st.chat_input("ENTER_COMMAND_OR_QUERY..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(f"> {prompt}")

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # EASTER EGG
        if "ahmad ali kala" in prompt.lower():
            full_response = "SYSTEM_LOG: Not a friend. Baat Bazaar me Rakhu ga Dukaaan Kholu ga."
        elif prompt.lower() in ["hi", "hello", "salam"]:
            full_response = "ACCESS_GRANTED. Hello! Kaise hain aap?"
        else:
            with st.status("INITIALIZING_AGENTIC_PROTOCOL...", expanded=True) as status:
                st.write("Intercepting live databases...")
                time.sleep(0.5)
                context = deep_research(prompt)
                
                sys_msg = f"You are OBITWICEX ELITE AGENT. Expert in Pakistan Law & Tech. Context: {context}. Speak in Roman Urdu like a pro consultant."
                messages = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-5:]
                
                response = client.chat.completions.create(
                    model="google/gemini-2.0-flash-lite-preview-02-05:free",
                    messages=messages,
                    stream=True
                )
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + " █")
                status.update(label="ANALYSIS_COMPLETE", state="complete")

        response_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
