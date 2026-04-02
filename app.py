import streamlit as st
from openai import OpenAI
import io, base64, requests

# --- [SECTION 1: CONFIG] ---
st.set_page_config(page_title="OBITWICEX | RECOVERY", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CSS - THE FINAL KILL-SWITCH FOR AUTOCORRECT] ---
st.markdown("""
    <style>
    .stApp { background-color: #010501; color: #FFFFFF; font-family: monospace; }
    /* KILLING SPELLCHECK AT THE ROOT */
    input { 
        background-color: #000 !important; 
        color: #00FF41 !important; 
        spellcheck: false !important;
        autocomplete: off !important;
        autocorrect: off !important;
    }
    div[data-testid="stChatMessage"] { background: rgba(0, 229, 255, 0.05); border-left: 3px solid #00E5FF; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- [SECTION 3: THE ENGINE] ---
def get_response(prompt):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"].strip()
        )
        # We send ONLY the current prompt to ensure NO history corruption
        res = client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            messages=[
                {"role": "system", "content": "You are OBITWICEX, a witty Lahori Yaar. No Filter. Talk in Roman Urdu/Punjabi."},
                {"role": "user", "content": prompt}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"NEURAL_LINK_ERROR: {str(e)}"

def draw_art(prompt):
    try:
        res = requests.post(
            url="https://openrouter.ai/api/v1/images/generations",
            headers={"Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY'].strip()}"},
            json={"prompt": prompt, "model": "stability-ai/sdxl"}
        )
        if res.status_code == 200: return res.json()["data"][0]["url"]
        return f"GEN_ERROR_{res.status_code}"
    except: return "GEN_FAIL"

# --- [SECTION 4: UI] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Top Tools
c1, c2 = st.columns(2)
with c1: voice = st.audio_input("🎙️")
with c2: scan = st.file_uploader("📸", type=['jpg','png'])

st.divider()

# Chat Display
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# THE CLEAN FORM (NO AUTOCORRECT)
with st.form("input_form", clear_on_submit=True):
    col_in, col_btn = st.columns([0.9, 0.1])
    with col_in:
        user_input = st.text_input("Type here, Sir...", label_visibility="collapsed")
    with col_btn:
        submit = st.form_submit_button("🚀")

if submit and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.write(user_input)
    
    with st.chat_message("assistant"):
        if any(x in user_input.lower() for x in ["draw", "image", "art"]):
            st.write("🛰️ Generating...")
            url = draw_art(user_input)
            if "http" in str(url):
                st.image(url)
                st.session_state.messages.append({"role": "assistant", "content": f"Image: {url}"})
            else: st.error(url)
        else:
            reply = get_response(user_input)
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
