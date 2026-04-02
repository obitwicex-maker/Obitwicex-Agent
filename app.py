import streamlit as st
from openai import OpenAI
import io, base64, requests

# --- [TACTICAL IMPORT CATCH] ---
try:
    import replicate
except Exception:
    st.warning("⚡ SYSTEM: INITIALIZING NEURAL LAYERS... REFRESH IN 30s.")
    st.stop()

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CSS - THE LAYOUT FIX] ---
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
    
    /* THE DOCK - FORCING INLINE */
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }
    
    /* Making File Uploader and Audio Input Compact */
    .stFileUploader section { padding: 0 !important; min-height: unset !important; }
    .stFileUploader label { display: none; }
    
    /* Styling the Text Input */
    .stTextInput input { 
        background: #000 !important; 
        color: #fff !important; 
        border: 1px solid #00E5FF !important; 
        border-radius: 20px !important; 
        padding-left: 15px !important;
    }
    .stTextInput input:focus { border-color: #00FF41 !important; box-shadow: 0 0 10px #00FF41 !important; }

    /* Fix column alignment */
    [data-testid="column"] { display: flex; align-items: center; justify-content: center; }

    header, footer {visibility: hidden;}
    </style>
    <div class="jarvis-hud"><div class="ring-1"></div></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: GEN ENGINES] ---
def gen_art(prompt):
    try:
        output = replicate.run("black-forest-labs/flux-dev", input={"prompt": prompt, "guidance_scale": 7.5})
        return output[0]
    except Exception: return None

def gen_motion(prompt):
    try:
        output = replicate.run("luma/ray", input={"prompt": prompt})
        return output
    except Exception: return None

# --- [SECTION 4: DOCK & HISTORY] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Container for messages to keep them above the dock
chat_placeholder = st.container()

with chat_placeholder:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            content = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
            st.markdown(content)

# THE SLIM DOCK
st.write("---")
with st.form("dock", clear_on_submit=True):
    # Adjusting column widths for a tighter fit
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
        except: st.error("VOICE_LINK_LOST")
    
    if final_prompt:
        st.session_state.messages.append({"role": "user", "content": final_prompt})
        with st.chat_message("assistant"):
            if any(x in final_prompt.lower() for x in ["draw", "image", "generate", "picture", "art"]):
                st.write("🎨 Uplink to Flux-Dev...")
                res = gen_art(final_prompt)
                if res:
                    st.image(res)
                    st.session_state.messages.append({"role": "assistant", "content": f"Generated Image: {res}"})
            elif any(x in final_prompt.lower() for x in ["video", "motion", "render", "clip"]):
                st.write("🎬 Uplink to Luma-Ray...")
                res = gen_motion(final_prompt)
                if res:
                    st.video(res)
                    st.session_state.messages.append({"role": "assistant", "content": f"Generated Video: {res}"})
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
