import streamlit as st
from openai import OpenAI
import io, base64, requests

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", layout="wide", initial_sidebar_state="collapsed")

# --- [TACTICAL IMPORT & ERROR BYPASS] ---
# We use a try-except at the top to ensure the app doesn't hang forever
try:
    import replicate
    GEN_READY = True
except Exception:
    GEN_READY = False

# --- [SECTION 2: CSS - THE FINAL UI HARDENING] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD RING */
    .jarvis-hud { display: flex; justify-content: center; align-items: center; height: 100px; margin-top: -10px; }
    .ring-1 { width: 80px; height: 80px; border: 2px solid #00E5FF; border-radius: 50%; border-top-color: transparent; animation: spin 10s linear infinite; box-shadow: 0 0 10px #00E5FF; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    /* CHAT BUBBLES */
    div[data-testid="stChatMessage"] { background: rgba(0, 229, 255, 0.03); border-left: 3px solid #00E5FF; margin-bottom: 8px; border-radius: 0 10px 10px 0; padding: 10px; }
    
    /* THE DOCK - NO BORDERS */
    [data-testid="stForm"] { border: none !important; padding: 0 !important; background: transparent !important; }
    
    /* COMPRESSION FOR LAYOUT */
    .stFileUploader section { padding: 0 !important; min-height: unset !important; border: 1px solid #00E5FF !important; }
    .stFileUploader label { display: none; }
    
    .stTextInput input { 
        background: #000 !important; 
        color: #fff !important; 
        border: 1px solid #00E5FF !important; 
        border-radius: 15px !important; 
    }
    .stTextInput input:focus { border-color: #00FF41 !important; box-shadow: 0 0 10px #00FF41 !important; }

    [data-testid="column"] { display: flex; align-items: center; justify-content: center; }
    header, footer { visibility: hidden; }
    </style>
    <div class="jarvis-hud"><div class="ring-1"></div></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: ENGINE LOGIC] ---
def gen_art(prompt):
    if not GEN_READY: return "SYSTEM_STILL_LOADING"
    try:
        output = replicate.run("black-forest-labs/flux-dev", input={"prompt": prompt, "guidance_scale": 7.5})
        return output[0]
    except: return None

def gen_motion(prompt):
    if not GEN_READY: return "SYSTEM_STILL_LOADING"
    try:
        output = replicate.run("luma/ray", input={"prompt": prompt})
        return output
    except: return None

# --- [SECTION 4: DOCK & HISTORY] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Show history
msg_container = st.container()
with msg_container:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            content = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
            st.markdown(content)

# Status bar if still loading
if not GEN_READY:
    st.info("⚠️ GEN-MODULES OFFLINE: Installing dependencies... Please wait.")

st.write("---")
# THE TACTICAL DOCK
with st.form("uplink_dock", clear_on_submit=True):
    c1, c2, c3, c4, c5 = st.columns([0.05, 0.1, 0.1, 0.65, 0.1])
    with c1: loc = st.checkbox("📍", label_visibility="collapsed")
    with c2: img_up = st.file_uploader("📸", type=['jpg','png'], label_visibility="collapsed")
    with c3: voice_in = st.audio_input("🎙️", label_visibility="collapsed")
    with c4: cmd = st.text_input("", placeholder="Command, Sir...", label_visibility="collapsed")
    with c5: push = st.form_submit_button("🚀")

# --- [SECTION 5: EXECUTION] ---
if push:
    final_prompt = cmd
    if voice_in:
        try:
            client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
            final_prompt = client_openai.audio.transcriptions.create(model="whisper-1", file=io.BytesIO(voice_in.read())).text
        except: st.error("VOICE_FAIL")
    
    if final_prompt:
        st.session_state.messages.append({"role": "user", "content": final_prompt})
        with st.chat_message("assistant"):
            low_p = final_prompt.lower()
            if any(x in low_p for x in ["draw", "image", "generate", "picture", "art"]):
                st.write("🎨 Uplink to Flux-Dev...")
                res = gen_art(final_prompt)
                if res == "SYSTEM_STILL_LOADING": st.warning("Gen-modules still arming. Wait 30s.")
                elif res:
                    st.image(res)
                    st.session_state.messages.append({"role": "assistant", "content": f"Image: {res}"})
            elif any(x in low_p for x in ["video", "motion", "render", "clip"]):
                st.write("🎬 Uplink to Luma-Ray...")
                res = gen_motion(final_prompt)
                if res == "SYSTEM_STILL_LOADING": st.warning("Gen-modules still arming. Wait 30s.")
                elif res:
                    st.video(res)
                    st.session_state.messages.append({"role": "assistant", "content": f"Video: {res}"})
            else:
                client_or = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
                stream = client_or.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet", 
                    messages=[{"role":"system","content":"You are OBITWICEX, a witty Lahori Yaar."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]], 
                    stream=True
                )
                full_reply = "".join([c.choices[0].delta.content for c in stream if c.choices[0].delta.content])
                st.markdown(full_reply)
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
            st.rerun()
