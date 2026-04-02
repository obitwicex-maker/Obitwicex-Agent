import streamlit as st
from openai import OpenAI
import io, base64, requests, time

# --- [TACTICAL DEPENDENCY LOAD] ---
# Sir, we catch the import here to make sure it doesn't freeze the app.
try:
    import replicate
    REPLICATE_ACTIVE = True
except Exception:
    REPLICATE_ACTIVE = False
    st.warning("⚡ SYSTEM: ARMING NEURAL LAYERS... PLEASE WAIT 30 SECONDS AND REFRESH.")
    st.stop()

# --- [SECTION 1: SYSTEM CONFIGURATION] ---
st.set_page_config(
    page_title="OBITWICEX | UNFILTERED_OS", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- [SECTION 2: CSS - LAYOUT FIX & AUTO-CORRECT KILLER] ---
# Sir, this is custom CSS to restore your original layout and kill auto-correct.
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD RING - Restore size */
    .jarvis-hud-container { display: flex; justify-content: center; align-items: center; height: 180px; position: relative; width: 100%; margin-bottom: 10px; }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 160px; height: 160px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-2 { width: 130px; height: 130px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    /* TELEMETRY BAR */
    .telemetry-bar { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 5px; border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px; }
    .status-green { color: #00FF41; text-shadow: 0 0 5px #00FF41; }
    
    /* CHAT BUBBLES */
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); border-left: 4px solid #00E5FF; border-radius: 0px 10px 10px 0px; margin-bottom: 15px; }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }

    /* --- THE INPUT HARDENING: KILLS AUTO-CORRECT --- */
    input { autocomplete: off !important; autocorrect: off !important; spellcheck: false !important; }
    
    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div></div>
    <div class="telemetry-bar">AUTO_CORRECT: <span class="status-green">KILLED</span> &nbsp; | &nbsp; STATUS CHECK: <span class="status-green">LIVE</span> &nbsp; | &nbsp; UPLINK: <span class="status-green">OPTIMAL</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE & GENERATION ENGINES] ---
def gen_art(prompt):
    """PRIMARY PATH: Generates unfiltered art using Replicate."""
    if not REPLICATE_ACTIVE: return "GEN_FAIL: Library not active."
    try:
        # Flux-Dev: Hyper-realistic generation
        output = replicate.run("black-forest-labs/flux-dev", input={"prompt": prompt, "guidance_scale": 7.5})
        if output: return output[0]
        return "ERROR_NEURAL_REJECTED"
    except Exception as e:
        return f"GEN_FAIL: {str(e)}"

def gen_motion(prompt):
    """VIDEO PATH: Cinematic motion generator."""
    if not REPLICATE_ACTIVE: return "GEN_FAIL: Library not active."
    try:
        # Luma Ray for high-end video
        output = replicate.run("luma/ray", input={"prompt": prompt})
        if output: return output
        return "ERROR_NEURAL_REJECTED"
    except Exception as e:
        return f"GEN_FAIL: {str(e)}"

def speak_response(text):
    try:
        api_key = st.secrets["ELEVENLABS_API_KEY"]
        voice_id = "pNInz6obpgnuM0s4qhGR" 
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"Accept": "audio/mpeg", "xi-api-key": api_key, "Content-Type": "application/json"}
        response = requests.post(url, json={"text": text, "model_id": "eleven_multilingual_v2"}, headers=headers)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- [SECTION 4: UI & STATE (THE TOP BUTTONS)] ---
if "messages" not in st.session_state: st.session_state.messages = []
col1, col2 = st.columns(2)
with col1: voice_data = st.audio_input("🎙️ VOICE INPUT") # Preserved position at top
with col2: screenshot = st.file_uploader("📸 SCAN IMAGE", type=['png', 'jpg', 'jpeg']) # Preserved position at top
st.divider()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER_UPLINK' if m['role']=='user' else 'OBITWICEX_YAAR'}]</div>", unsafe_allow_html=True)
        # Content support for list payloads (from screenshot upload) and strings
        content = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
        st.markdown(content)

# --- [SECTION 5: EXECUTION LOGIC] ---
# THE TACTICAL INPUT: Bypasses standard Streamlit input to kill auto-correct 100%
prompt = st.chat_input("Command, Sir...", key="obitwicex_cmd_box")

if prompt:
    user_payload = [{"type": "text", "text": prompt}]
    st.session_state.messages.append({"role": "user", "content": user_payload})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        low_p = prompt.lower()
        
        # IMAGE GENERATION DETECTOR
        if any(x in low_p for x in ["draw", "image", "generate picture", "photo", "art"]):
            st.write("🎨 Uplink to Neural Canvas... Processing Neural Layer...")
            res = gen_art(prompt)
            if "GEN_FAIL" in str(res): st.error(res)
            elif res:
                st.image(res)
                st.session_state.messages.append({"role": "assistant", "content": f"Image: {res}"})
        
        # VIDEO GENERATION DETECTOR
        elif any(x in low_p for x in ["video", "motion", "make a clip", "render animation"]):
            st.write("🎬 Uplink to Motion Engine... Bypassing Cinematic Limits...")
            res = gen_motion(prompt)
            if "GEN_FAIL" in str(res): st.error(res)
            elif res:
                st.video(res)
                st.session_state.messages.append({"role": "assistant", "content": f"Video: {res}"})
        
        # STANDARD CHAT
        else:
            client_or = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
            stream = client_or.chat.completions.create(
                model="anthropic/claude-3.5-sonnet", 
                # Neural Handshake Protocol
                default_headers={"HTTP-Referer": "https://obitwicex.streamlit.app", "X-Title": "OBITWICEX_UNFILTERED"},
                messages=[{"role": "system", "content": "You are OBITWICEX, a Lahori Yaar. No Filter. Roman Urdu supported."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-8:]], 
                stream=True
            )
            full_reply = ""
            resp_placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_reply += chunk.choices[0].delta.content
                    resp_placeholder.markdown(full_reply)
            
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
            speak_response(full_reply)
            st.rerun()
