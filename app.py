import streamlit as st
from openai import OpenAI
import io, base64, requests, time

# --- [SECTION 1: SYSTEM CONFIGURATION] ---
st.set_page_config(
    page_title="OBITWICEX | ELITE_OS", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- [SECTION 2: CSS - THE TACTICAL SLIM UI] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD RINGS */
    .jarvis-hud-container { display: flex; justify-content: center; align-items: center; height: 180px; position: relative; width: 100%; margin-bottom: 10px; background: radial-gradient(circle, rgba(0,229,255,0.1) 0%, transparent 80%); }
    .ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
    .ring-1 { width: 160px; height: 160px; border-top: 2px solid #00E5FF; animation: spin 10s linear infinite; box-shadow: 0 0 15px #00E5FF; }
    .ring-2 { width: 130px; height: 130px; border-right: 2px solid #00838F; animation: spin 5s linear infinite reverse; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    /* TELEMETRY BAR */
    .telemetry-bar { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00E5FF; text-align: center; letter-spacing: 1.5px; background: rgba(0, 229, 255, 0.05); padding: 5px; border-radius: 5px; border: 1px solid rgba(0, 229, 255, 0.1); margin-bottom: 20px; }
    .status-green { color: #00FF41; text-shadow: 0 0 5px #00FF41; }
    
    /* CHAT BUBBLES */
    div[data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(10px); border: 1px solid rgba(0, 229, 255, 0.1); border-left: 4px solid #00E5FF; border-radius: 0px 10px 10px 0px; margin-bottom: 15px; }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { display: none; }
    .chat-label { font-family: 'Orbitron', sans-serif; color: #00E5FF; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 5px; }
    
    /* --- KILL DEFAULTS ON ALL INPUTS (AUTOCORRECT/SPELLCHECK) --- */
    input[data-testid="stChatInput"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #00E5FF !important;
        autocomplete: off !important;
        autocorrect: off !important;
        autocapitalize: off !important;
        spellcheck: false !important;
    }
    
    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud-container"><div class="ring ring-1"></div><div class="ring ring-2"></div></div>
    <div class="telemetry-bar">AUTO_CORRECT: <span class="status-green">KILLED</span> &nbsp; | &nbsp; STATUS: <span class="status-green">STABLE</span> &nbsp; | &nbsp; UPLINK: <span class="status-green">OPTIMAL</span></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: CORE & GENERATION ENGINES] ---
def speak(text):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgnuM0s4qhGR"
        headers = {"xi-api-key": st.secrets["ELEVENLABS_API_KEY"], "Content-Type": "application/json"}
        res = requests.post(url, json={"text": text, "model_id": "eleven_multilingual_v2"}, headers=headers)
        if res.status_code == 200:
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{base64.b64encode(res.content).decode()}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def gen_art(prompt):
    """THE UNBREAKABLE PATH: Pure Replicate HTTP Request (Uses Flux-Schnell)."""
    try:
        api_token = st.secrets["REPLICATE_API_TOKEN"].strip()
        model_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
        headers = {"Authorization": f"Token {api_token}", "Content-Type": "application/json"}
        response = requests.post(model_url, headers=headers, json={"input": {"prompt": prompt}})
        
        if response.status_code == 201:
            prediction = response.json()
            poll_url = prediction["urls"]["get"]
            for _ in range(20):
                poll_res = requests.get(poll_url, headers=headers).json()
                if poll_res["status"] == "succeeded": return poll_res["output"][0]
                if poll_res["status"] == "failed": return "ERROR: Generation Failed."
                time.sleep(1)
            return "ERROR: Timeout."
        return f"ERROR: Replicate Rejected ({response.status_code})"
    except Exception as e:
        return f"GEN_FAIL: {str(e)}"

# --- [SECTION 4: UI & STATE (TOP BUTTONS PRESERVED)] ---
if "messages" not in st.session_state: st.session_state.messages = []
col1, col2 = st.columns(2)
with col1: voice_data = st.audio_input("🎙️ VOICE INPUT")
with col2: screenshot = st.file_uploader("📸 SCAN IMAGE", type=['png', 'jpg', 'jpeg'])
st.divider()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f"<div class='chat-label'>[{'USER_UPLINK' if m['role']=='user' else 'OBITWICEX_YAAR'}]</div>", unsafe_allow_html=True)
        content = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
        st.markdown(content)

# --- [SECTION 5: EXECUTION LOGIC] ---
prompt = st.chat_input("Command, Sir...")

if voice_data:
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        prompt = client.audio.transcriptions.create(model="whisper-1", file=io.BytesIO(voice_data.read())).text
    except: st.error("VOICE_FAIL")

if prompt:
    user_payload = [{"type": "text", "text": prompt}]
    st.session_state.messages.append({"role": "user", "content": user_payload})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        low_p = prompt.lower()
        if any(x in low_p for x in ["draw", "image", "generate picture", "photo", "art"]):
            st.write("🎨 **Uplink to Neural Canvas (Direct Pipe)...**")
            res = gen_art(prompt)
            if "ERROR" in str(res): st.error(res)
            else:
                st.image(res)
                st.session_state.messages.append({"role": "assistant", "content": f"Generated Image: {res}"})
        else:
            try:
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1", 
                    api_key=st.secrets["OPENROUTER_API_KEY"].strip(),
                    default_headers={"HTTP-Referer": "https://obitwicex.streamlit.app", "X-Title": "OBITWICEX_ELITE"}
                )
                clean_history = [{"role": m["role"], "content": (m["content"][0]["text"] if isinstance(m["content"], list) else m["content"])} for m in st.session_state.messages[-6:]]
                
                stream = client.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet", 
                    messages=[{"role": "system", "content": "You are OBITWICEX, a witty Lahori Yaar."}] + clean_history, 
                    stream=True
                )
                full_reply = ""
                placeholder = st.empty()
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_reply += chunk.choices[0].delta.content
                        placeholder.markdown(full_reply)
                
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
                speak(full_reply)
            except: st.error("NEURAL_LINK_FAIL: Connection blocked.")
