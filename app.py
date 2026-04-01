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
    code { background-color: #161B22 !important; color: #79C0FF !important; border-radius: 6px; padding: 2px 4px; border: 1px solid #30363D; }
    div[data-testid="stChatMessage"] { 
        border-radius: 12px; 
        border: 1px solid #30363D; 
        background-color: #161B22; 
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTONOMOUS RESEARCH ENGINE (PAKISTAN FOCUSED) ---
def deep_research(query):
    try:
        with DDGS() as ddgs:
            pak_query = f"{query} site:sindhhighcourt.gov.pk OR site:lhc.gov.pk OR site:pakistanlawsite.com OR site:fbr.gov.pk OR site:secp.gov.pk"
            results = [r for r in ddgs.text(pak_query, max_results=6)]
            if not results:
                results = [r for r in ddgs.text(f"{query} Pakistan Law Judgment 2026", max_results=5)]
            return "\n\n".join([f"ANALYSIS SOURCE: {r['title']}\n{r['body']}" for r in results])
    except: 
        return "Internal Knowledge Base Active."

# Use Streamlit Secrets for the API Key
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

if "messages" not in st.session_state: 
    st.session_state.messages = []

with st.sidebar:
    st.title("Obitwicex Control ⚡")
    st.write("---")
    st.status("Specialist Protocols: **ONLINE**", state="complete")
    st.info("Expert: Law (SHC/LHC), Real Estate, E-Commerce, Dev & SEO.")
    if st.button("Purge System Cache"):
        st.session_state.messages = []
        st.rerun()

# --- 3. CHAT DISPLAY ---
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 4. THE REASONING ENGINE ---
if prompt := st.chat_input("Submit Task, Legal Query, or Code..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        full_response = ""
        
        # --- THE EASTER EGG ---
        if "ahmad ali kala" in prompt.lower():
            full_response = "Not a Friend Definitely Not a person to To be Around with In Simple Words ( Tumhe laga tha kuch kahu ga nahi Me to Baat Bazaar me Rakhu ga Dukaaan Kholu ga)"
            response_placeholder.markdown(full_response)
        
        # --- THE PROFESSIONAL GREETING ---
        elif prompt.lower() in ["hi", "hello", "hey", "salam"]:
            full_response = "Hello! Kaise hain aap?"
            response_placeholder.markdown(full_response)
            
        else:
            expert_terms = ["9c", "law", "judgment", "fbr", "secp", "reit", "property", "fix", "code", "seo", "ads", "strategy", "theek", "theek hu"]
            is_expert_query = any(k in prompt.lower() for k in expert_terms) or len(prompt.split()) > 4

            if is_expert_query:
                with st.status(":material/terminal: Executing Agentic Reasoning...", expanded=True) as status:
                    st.write("Syncing with live Pakistan Law & Market databases...")
                    live_context = deep_research(prompt)
                    sys_msg = f"""You are Obitwicex Elite Agent.
                    - GREETINGS: Professional and natural. If user says 'theek hu', reply like 'Zabardast! Bataiye aaj main aapki kis technical ya legal maslay mein madad kar sakta hoon?'
                    - EXPERTISE: Pakistan Law (SHC/LHC), Real Estate, E-Commerce, Full-Stack Dev.
                    - CONTEXT: {live_context}
                    - LANGUAGE: Roman Urdu for advice, English for code/citations. NO ARABIC SCRIPT. NO WEIRD POETRY."""
                    
                    messages = [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:]
                    # FIXED MODEL CALL 1
                    response = client.chat.completions.create(model="google/gemini-2.0-flash-lite-preview-02-05:free", messages=messages, stream=True)
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            response_placeholder.markdown(full_response + " ▋")
                    status.update(label="Analysis Delivered", state="complete", expanded=False)
