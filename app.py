import streamlit as st
from openai import OpenAI
import io, base64, requests

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CSS - THE LAYOUT RESTORER & AUTOCORRECT KILLER] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD RINGS RESTORED */
    .jarvis-hud-container { display: flex; justify-content: center; align-items: center; height: 180px; position: relative; width: 100%; margin-bottom: 10px; }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 160px; height: 160px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-2 { width: 130px; height: 130px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    /* CHAT BUBBLES */
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); border-left: 4px solid #00E5FF; border-radius: 0 10px 10px 0; margin-bottom: 15px; }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; }

    /* --- THE UNFILTERED INPUT: HARD KILLS AUTOCORRECT --- */
    textarea {
        background-color: #000000 !important;
        color: #00FF41 !important;
        border: 1px solid #00E5FF !important;
        spellcheck: false !important;
        autocomplete: off !important;
        autocorrect: off !important;
    }
    
    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: THE ENGINES] ---
def gen_art(prompt):
    try:
        # Using a reliable image model via OpenRouter
        res = requests.post(
            url="https://openrouter.ai/api/v1/images/generations",
            headers={"Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY'].strip()}"},
            json={"prompt": prompt, "model": "stability-ai/sdxl"}
        )
        return res.json()["data"][0]["url"] if res.status_code == 200 else f"GEN_FAIL_{res.status_code}"
    except: return "GEN_ERROR"

# --- [SECTION 4: UI] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Top Tools (Your Original Layout)
c1, c2 = st.columns(2)
with c1: voice = st.audio_input("🎙️ VOICE")
with c2: scan = st.file_uploader("📸 SCAN", type=['jpg','png'])
st.divider()

# Chat display
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER' if m['role']=='user' else 'OBITWICEX'}]</div>", unsafe_allow_html=True)
        st.markdown(m["content"])

# --- [SECTION 5: THE TACTICAL INPUT FORM] ---
with st.form("uplink", clear_on_submit=True):
    # Using text_area as it supports the 'spellcheck' parameter better in browsers
    user_input = st.text_area("Command, Sir...", label_visibility="collapsed", height=60)
    submitted = st.form_submit_button("🚀 INITIATE STRIKE")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        if any(x in user_input.lower() for x in ["draw", "image", "art"]):
            st.write("🛰️ Generating art...")
            url = gen_art(user_input)
            if "http" in str(url):
                st.image(url)
                st.session_state.messages.append({"role": "assistant", "content": f"Generated: {url}"})
            else: st.error(url)
        else:
            try:
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
                # Switched to GPT-4o-mini for maximum stability on OpenRouter
                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[{"role": "system", "content": "You are OBITWICEX, a witty Lahori Yaar. Speak in Roman Urdu/Punjabi."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-4:]]
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            except Exception as e:
                st.error(f"NEURAL_FAIL: {str(e)}")
