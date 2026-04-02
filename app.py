import streamlit as st
from openai import OpenAI
import io, base64, requests

# --- [TACTICAL DEPENDENCY LOAD] ---
try:
    import replicate
except Exception as e:
    st.warning("⚡ SYSTEM: CONFIGUREING NEURAL LAYERS... PLEASE REFRESH IN 30 SECONDS.")
    st.stop()

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CSS - TACTICAL UI] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    .jarvis-hud { display: flex; justify-content: center; align-items: center; height: 120px; margin-top: -20px; }
    .ring-1 { width: 100px; height: 100px; border: 2px solid #00E5FF; border-radius: 50%; border-top-color: transparent; animation: spin 10s linear infinite; box-shadow: 0 0 10px #00E5FF; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    div[data-testid="stChatMessage"] { background: rgba(0, 229, 255, 0.03); border-left: 3px solid #00E5FF; margin-bottom: 8px; border-radius: 0 10px 10px 0; }
    .stTextInput input { background: #000 !important; color: #fff !important; border: 1px solid #00E5FF !important; border-radius: 10px !important; }
    .stTextInput input:focus { border-color: #00FF41 !important; box-shadow: 0 0 10px #00FF41 !important; }
    header, footer {visibility: hidden;}
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }
    </style>
    <div class="jarvis-hud"><div class="ring-1"></div></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: GENERATION ENGINES] ---
def gen_art(prompt):
    try:
        # Flux-Dev for hyper-realistic, uncensored generation
        output = replicate.run("black-forest-labs/flux-dev", input={"prompt": prompt, "guidance_scale": 7.5})
        return output[0]
    except Exception as e:
        st.error(f"IMAGE_GEN_ERROR: {str(e)}")
        return None

def gen_motion(prompt):
    try:
        # Luma Ray for high-end cinematic video
        output = replicate.run("luma/ray", input={"prompt": prompt})
        return output
    except Exception as e:
        st.error(f"VIDEO_GEN_ERROR: {str(e)}")
        return None

# --- [SECTION 4: DOCK & HISTORY] ---
if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        # Support for both list-style and string-style message content
        content = m['content'][0]['text'] if isinstance(m['content'], list) else m['content']
        st.markdown(content)

st.write("---")
with st.form("dock", clear_on_submit=True):
    c1, c2, c3, c4, c5 = st.columns([0.1, 0.1, 0.1, 0.6, 0.1])
    with c1: loc = st.checkbox("📍", label_visibility="collapsed")
    with c2: img_up = st.file_uploader("📸", type=['jpg','png'], label_visibility="collapsed")
    with c3: voice_in = st.audio_input("🎙️", label_visibility="collapsed")
    with c4: cmd = st.text_input("", placeholder="Draw... / Make a video...", label_visibility="collapsed")
    with c5: push = st.form_submit_button("🚀")

# --- [SECTION 5: ROUTING & EXECUTION] ---
if push:
    final_prompt = cmd
    if voice_in:
        client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        final_prompt = client_openai.audio.transcriptions.create(model="whisper-1", file=io.BytesIO(voice_in.read())).text
    
    if final_prompt:
        st.session_state.messages.append({"role": "user", "content": final_prompt})
        with st.chat_message("assistant"):
            # Detecting generation keywords automatically
            if any(x in final_prompt.lower() for x in ["draw", "image", "generate", "picture", "photo", "art"]):
                res = gen_art(final_prompt)
                if res:
                    st.image(res)
                    st.session_state.messages.append({"role": "assistant", "content": f"Image generated: {res}"})
            elif any(x in final_prompt.lower() for x in ["video", "motion", "render", "clip"]):
                res = gen_motion(final_prompt)
                if res:
                    st.video(res)
                    st.session_state.messages.append({"role": "assistant", "content": f"Video generated: {res}"})
            else:
                # Standard Neural Chat
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
