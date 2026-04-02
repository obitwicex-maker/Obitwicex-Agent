import streamlit as st
from openai import OpenAI
import io, base64, requests

# --- [SECTION 1: SYSTEM CONFIGURATION] ---
st.set_page_config(
    page_title="OBITWICEX | ELITE_OS", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- [SECTION 2: CSS - THE AUTO-CORRECT EXECUTIONER] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    .jarvis-hud-container { display: flex; justify-content: center; align-items: center; height: 180px; position: relative; width: 100%; margin-bottom: 10px; }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 160px; height: 160px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-2 { width: 130px; height: 130px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    .telemetry-bar { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 5px; border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px; }
    
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); border-left: 4px solid #00E5FF; border-radius: 0 10px 10px 0; margin-bottom: 15px; }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }

    /* HARD KILL AUTO-CORRECT ON ALL INPUTS */
    input {
        background-color: #000000 !important;
        color: #00FF41 !important;
        border: 1px solid #00E5FF !important;
        autocomplete: off !important;
        autocorrect: off !important;
        autocapitalize: off !important;
        spellcheck: false !important;
    }
    
    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div></div>
    <div class="telemetry-bar">AUTO_CORRECT: <span style="color:#FF3131">TERMINATED</span> | UPLINK: <span style="color:#00FF41">REINFORCED</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: ENGINE LOGIC] ---
def speak(text):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR"
        headers = {"xi-api-key": st.secrets["ELEVENLABS_API_KEY"], "Content-Type": "application/json"}
        res = requests.post(url, json={"text": text, "model_id": "eleven_multilingual_v2"}, headers=headers)
        if res.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(res.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def gen_art(prompt):
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"].strip()
        # Using the standard SDXL for absolute compatibility
        res = requests.post(
            url="https://openrouter.ai/api/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"prompt": prompt, "model": "stability-ai/sdxl"}
        )
        if res.status_code == 200: return res.json()["data"][0]["url"]
        return f"ERROR_{res.status_code}"
    except: return "GEN_FAIL"

# --- [SECTION 4: UI & STATE] ---
if "messages" not in st.session_state: st.session_state.messages = []
c1, c2 = st.columns(2)
with col1: voice_data = st.audio_input("🎙️ VOICE")
with col2: screenshot = st.file_uploader("📸 SCAN", type=['png', 'jpg', 'jpeg'])
st.divider()

# Display Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER' if m['role']=='user' else 'OBITWICEX'}]</div>", unsafe_allow_html=True)
        st.markdown(m['content'][0]['text'] if isinstance(m['content'], list) else m['content'])

# --- [SECTION 5: THE NUCLEAR INPUT BOX] ---
# Sir, we are using a form to replace st.chat_input so we can kill auto-correct 100%
with st.form("command_center", clear_on_submit=True):
    cmd_col, btn_col = st.columns([0.9, 0.1])
    with cmd_col:
        # Standard text input with no spellcheck allowed
        prompt = st.text_input("Command, Sir...", label_visibility="collapsed", key="user_cmd")
    with btn_col:
        submit = st.form_submit_button("🚀")

if submit and prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        low_p = prompt.lower()
        if any(x in low_p for x in ["draw", "image", "art", "photo"]):
            st.write("🎨 Uplink to Neural Canvas...")
            res = gen_art(prompt)
            if "ERROR" in str(res): st.error(f"Image API Error: {res}")
            else:
                st.image(res); st.session_state.messages.append({"role": "assistant", "content": f"Image: {res}"})
        else:
            try:
                # REINFORCED CHAT CALL
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1", 
                    api_key=st.secrets["OPENROUTER_API_KEY"].strip()
                )
                # Hardcoded history cleaning to prevent BadRequest errors
                clean_history = [{"role": m["role"], "content": (m["content"][0]["text"] if isinstance(m["content"], list) else m["content"])} for m in st.session_state.messages[-5:]]
                
                response = client.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet", 
                    messages=[{"role": "system", "content": "You are OBITWICEX, a witty Lahori Yaar. Speak in Roman Urdu/Punjabi."}] + clean_history,
                )
                reply = response.choices[0].message.content
                st.markdown(f"<div class='chat-label'>[OBITWICEX]</div>\n\n{reply}", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                speak(reply)
                st.rerun()
            except Exception as e:
                st.error(f"NEURAL_LINK_FAIL: {str(e)}")
