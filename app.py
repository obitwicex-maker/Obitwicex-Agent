import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# --- 1. PRO AGENT UI & TERMINAL STYLING ---
st.set_page_config(page_title="Obitwicex Elite Agent", page_icon="🤖", layout="wide")
load_dotenv()

st.markdown("""
    <style>
    .stApp { background-color: #0D1117; }
    .stMarkdown p { font-family: 'Inter', sans-serif; font-size: 14px; color: #C9D1D9; line-height: 1.6; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTONOMOUS RESEARCH ENGINE ---
def deep_research(query):
    try:
        with DDGS() as ddgs:
            pak_query = f"{query} site:sindhhighcourt.gov.pk OR site:lhc.gov.pk OR site:fbr.gov.pk"
            results = [r for r in ddgs.text(pak_query, max_results=5)]
            return "\n\n".join([f"SOURCE: {r['title']}\n{r['body']}" for r in results])
    except: 
        return "Internal Knowledge Base Active."

# --- 3. THE BRAIN (WITH REQUIRED OPENROUTER HEADERS) ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
    default_headers={
        "HTTP-Referer": "https://streamlit.app", # Required by OpenRouter
        "X-Title": "Obitwicex Agent"            # Required by OpenRouter
    }
)

if "messages" not in st.session_state: 
    st.session_state.messages = []

with st.sidebar:
    st.title("Obitwicex Control ⚡")
    st.info("Expert: Law, Real Estate, Dev & SEO.")
    if st.button("Purge System Cache"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CHAT DISPLAY ---
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 5. THE REASONING ENGINE ---
if prompt := st.chat_input("Submit Task..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        full_response = ""
        
        if "ahmad ali kala" in prompt.lower():
            full_response = "Tumhe laga tha kuch kahu ga nahi Me to Baat Bazaar me Rakhu ga Dukaaan Kholu ga."
        elif prompt.lower() in ["hi", "hello", "salam"]:
            full_response = "Hello! Kaise hain aap?"
        else:
            with st.status("Executing Agentic Reasoning...", expanded=True) as status:
                live_context = deep_research(prompt)
                sys_msg = f"You are Obitwicex. Expert in Pakistan Law & Tech. Context: {live_context}. Use Roman Urdu."
                messages = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-5:]
                
                # Using a very stable model
                response = client.chat.completions.create(
                    model="google/gemini-2.0-flash-lite-preview-02-05:free",
                    messages=messages,
                    stream=True
                )
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + " ▋")
                status.update(label="Complete", state="complete")

        response_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
