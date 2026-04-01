import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import time

# --- 1. ELITE TERMINAL STYLING ---
st.set_page_config(page_title="OBITWICEX | ELITE_AGENT", page_icon="⚡", layout="wide")
load_dotenv()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    .stApp { background-color: #050505; }
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2 { 
        font-family: 'Fira Code', monospace; 
        color: #00FF41 !important; 
    }
    div[data-testid="stChatMessage"] { 
        background-color: rgba(10, 10, 10, 0.9);
        border: 1px solid #00FF41;
        border-radius: 4px;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE STABLE BRAIN (PAID CONNECTION) ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
    default_headers={
        "HTTP-Referer": "https://obitwicex.com", 
        "X-Title": "Obitwicex Elite Agent"
    }
)

# --- 3. SEARCH ENGINE ---
def deep_research(query):
    try:
        with DDGS() as ddgs:
            pak_query = f"{query} Pakistan site:sindhhighcourt.gov.pk OR site:lhc.gov.pk OR site:fbr.gov.pk"
            results = [r for r in ddgs.text(pak_query, max_results=3)]
            return "\n\n".join([f"SOURCE: {r['title']}\n{r['body']}" for r in results])
    except: 
        return "LOCAL_ENCRYPTED_DB_ACTIVE"

# --- 4. SESSION MANAGEMENT (CLEAN SLATE) ---
if "messages" not in st.session_state: 
    st.session_state.messages = []

with st.sidebar:
    st.title("⚡ OBITWICEX_CTRL")
    st.code("UPLINK: ACTIVE\nSTATUS: ENCRYPTED", language="bash")
    if st.button("PURGE_ALL_SYSTEM_LOGS"):
        st.session_state.messages = []
        st.rerun()

# Display ONLY what is actually in the message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. THE ENGINE ---
if prompt := st.chat_input("ENTER_COMMAND_OR_QUERY..."):
    # Immediately add user message to state so it shows up correctly
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(f"> {prompt}")

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # LOGIC FOR SPECIFIC COMMANDS
        prompt_low = prompt.lower()
        if "ahmad ali kala" in prompt_low:
            full_response = "LOG: Not a friend. Baat Bazaar me Rakhu ga Dukaaan Kholu ga."
        elif prompt_low in ["hi", "hello", "hey", "salam"]:
            full_response = "ACCESS_GRANTED. Hello! Main Obitwicex Elite Agent hoon. Bataiye aaj kis maslay mein madad karoon?"
        else:
            with st.status("INITIALIZING_EXPERT_PROTOCOL...", expanded=True) as status:
                st.write("Intercepting live databases...")
                context = deep_research(prompt)
                sys_msg = f"You are OBITWICEX ELITE AGENT. Expert in Pakistan Law & Tech. Context: {context}. Speak in Roman Urdu like a high-level pro."
                
                # Using a high-stability paid model to bypass those 400/401 errors
                messages = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-5:]
                
                response = client.chat.completions.create(
                    model="meta-llama/llama-3.3-70b-instruct",
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
