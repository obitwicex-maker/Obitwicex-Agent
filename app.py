import streamlit as st
from openai import OpenAI
import io, base64, requests, replicate

# --- [SECTION 1: SYSTEM CONFIG] ---
st.set_page_config(page_title="OBITWICEX | ELITE_OS", layout="wide", initial_sidebar_state="collapsed")

# --- [SECTION 2: CSS - THE RED LINE KILLER] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #010501; color: #FFFFFF; font-family: 'Fira Code', monospace; }
    
    /* HUD RINGS */
    .jarvis-hud { display: flex; justify-content: center; align-items: center; height: 120px; margin-top: -20px; }
    .ring-1 { width: 100px; height: 100px; border: 2px solid #00E5FF; border-radius: 50%; border-top-color: transparent; animation: spin 10s linear infinite; box-shadow: 0 0 10px #00E5FF; }
    @keyframes spin { 100% { transform: rotate(360deg); } }

    /* CHAT BUBBLES */
    div[data-testid="stChatMessage"] { background: rgba(0, 229, 255, 0.03); border-left: 3px solid #00E5FF; margin-bottom: 8px; border-radius: 0 10px 10px 0; }
    
    /* THE DOCK - NO RED BORDERS */
    .stTextInput input { background: #000 !important; color: #fff !important; border: 1px solid #00E5FF !important; border-radius: 10px !important; }
    .stTextInput input:focus { border-color: #00FF41 !important; box-shadow: 0 0 10px #00FF41 !important; }
    
    header, footer {visibility: hidden;}
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }
    </style>
    <div class="jarvis-hud"><div class="ring-1"></div></div>
    """, unsafe_allow_html=True)

# --- [SECTION 3: GENERATION ENGINES (UNCENSORED)] ---
def gen_art(prompt):
    try:
        # Flux-Dev: High-end realism, minimal censorship via Replicate
        output = replicate.run("black-forest-labs/flux-dev", input={"prompt": prompt, "guidance_scale": 7.5})
        return output[0]
    except: return None

def gen_motion(prompt):
    try:
        # Luma Ray: Advanced cinematic video generation
        output = replicate.run("luma/ray", input={"prompt": prompt})
        return output
    except: return None

def speak(text):
    try:
        api = st.secrets["ELEVENLABS_API_KEY"].strip()
        res = requests.post("https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM", 
            json={"text": text, "model_id": "eleven_multilingual_v2"}, 
            headers={"xi-api-key": api, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        if res.status_code == 200:
            b64 = base64.b64encode(res.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- [SECTION 4: TACTICAL DOCK & HISTORY] ---
if "messages" not in st.session_state: st.session_state.messages = []

# Render history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m['content'][0]['text'] if isinstance(m['content'], list) else m['content'])

st.write("---")
# THE TACTICAL INPUT FORM (SENDS ON ENTER)
with st.form("dock", clear_on_submit=True):
    c1, c2, c3, c4, c5 = st.columns([0.1, 0.1, 0.1, 0.6, 0.1])
    with c1: loc = st.checkbox("📍", label_visibility="collapsed")
    with c2: img_upload = st.file_uploader("📸", type=['jpg','png'], label_visibility="collapsed")
    with c3: voice_in = st.audio_input("🎙️", label_visibility="collapsed")
    with c4: cmd = st.text_input("", placeholder="Draw me... / Make a video of...", label_visibility="collapsed")
    with c5: push = st.form_submit_button("🚀")

# --- [SECTION 5: INTENT ROUTING & EXECUTION] ---
if push:
    final_prompt = cmd
    if voice_in:
        client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())
        final_prompt = client_openai.audio.transcriptions.create(model="whisper-1", file=io.BytesIO(voice_in.read())).text
    
    if final_prompt:
        st.session_state.messages.append({"role": "user", "content": final_prompt})
        
        with st.chat_message("assistant"):
            # ROUTER: DETECT INTENT AUTOMATICALLY
            img_triggers = ["draw", "image", "generate", "picture", "photo", "art"]
            vid_triggers = ["video", "motion", "make a clip", "render", "animation"]

            if any(x in final_prompt.lower() for x in img_triggers):
                st.write("🎨 **Uplink to Flux-Dev... Processing Unfiltered Neural Layer...**")
                res = gen_art(final_prompt)
                if res:
                    st.image(res)
                    st.session_state.messages.append({"role": "assistant", "content": f"Image: {res}"})
                else: st.error("GEN_FAIL")
            
            elif any(x in final_prompt.lower() for x in vid_triggers):
                st.write("🎬 **Uplink to Luma-Ray... Bypassing Cinematic Limits...**")
                res = gen_motion(final_prompt)
                if res:
                    st.video(res)
                    st.session_state.messages.append({"role": "assistant", "content": f"Video: {res}"})
                else: st.error("GEN_FAIL")
            
            else:
                # Standard Chat Logic
                client_or = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_API_KEY"].strip())
                stream = client_or.chat.completions.create(
                    model="anthropic/claude-3.5-sonnet", 
                    messages=[{"role":"system","content":"You are OBITWICEX, a witty Lahori Yaar."}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]], 
                    stream=True
                )
                full_reply = "".join([c.choices[0].delta.content for c in stream if c.choices[0].delta.content])
                st.markdown(full_reply)
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
                speak(full_reply)
            
            st.rerun()
