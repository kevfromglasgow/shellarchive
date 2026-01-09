import streamlit as st
import streamlit.components.v1 as components
import json
import requests
from io import BytesIO
import base64
import random

# ---------------- CONFIG ----------------
GLB_MODEL_URL = "https://raw.githubusercontent.com/kevfromglasgow/shellarchive/main/shell.glb"

st.set_page_config(
    page_title="SYSTEM_DATA // XLS",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STATE ----------------
if "manual_launch" not in st.session_state:
    st.session_state.manual_launch = False

if "current_track" not in st.session_state:
    st.session_state.current_track = None

if "shuffle_mode" not in st.session_state:
    st.session_state.shuffle_mode = False

# ---------------- CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.stApp {
    background-color: #000;
    color: #00FF00;
    font-family: 'Share Tech Mono', monospace;
}

.block-container { 
    padding-top: 0; 
    padding-bottom: 0; 
    max-width: 100%; 
}

header, footer { visibility: hidden; }

.terminal-header {
    border: 2px solid #00FF00;
    padding: 15px;
    margin-bottom: 20px;
    background: rgba(0, 20, 0, 0.8);
}

.blink { animation: blink 1s step-start infinite; }
@keyframes blink { 50% { opacity: 0; } }

.sheet-container {
    border: 2px solid #00FF00;
    background: rgba(0, 10, 0, 0.9);
}

.sheet-header {
    display: flex;
    border-bottom: 2px double #00FF00;
    background: rgba(0, 50, 0, 0.6);
    padding: 12px 0;
    font-weight: bold;
}

.sheet-row {
    border-bottom: 1px solid #003300;
    min-height: 45px;
    display: flex;
    align-items: stretch;
}

.sheet-row:hover {
    background: rgba(0, 255, 0, 0.1);
    border-left: 4px solid #00FF00;
}

.cell {
    padding: 0 10px;
    display: flex;
    align-items: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.col-a { border-right: 1px solid #00FF00; color: #00AA00; justify-content: center; }
.col-b { border-right: 1px solid #00FF00; width: 100%; }
.col-c { border-right: 1px solid #00FF00; color: #00DD00; }
.col-d { justify-content: center; font-weight: bold; }

.stButton button {
    border: none;
    background: transparent;
    color: #00FF00;
    text-align: left;
    width: 100%;
    font-family: 'Share Tech Mono', monospace;
}

.stButton button:hover {
    color: #FFFFFF;
    text-shadow: 0 0 8px rgba(255,255,255,0.8);
}

.active-row {
    background: rgba(0,255,0,0.2) !important;
    border-left: 4px solid #00FF00;
}

.status-playing { 
    color: #00FF00; 
    text-shadow: 0 0 10px rgba(0,255,0,0.8);
    animation: pulse 1.5s infinite; 
}

@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.6;} }

.close-btn button {
    border: 1px solid #00FF00 !important;
}

.close-btn button:hover {
    background: #00FF00 !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
@st.cache_data
def load_secure_playlist():
    try:
        if "PLAYLIST_DATA" in st.secrets:
            return json.loads(st.secrets["PLAYLIST_DATA"])
        return []
    except:
        return []

@st.cache_data(show_spinner=False)
def fetch_audio_bytes(url):
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        return r.content
    except:
        return None

playlist = load_secure_playlist()

# ---------------- AUDIO ----------------
def render_custom_player(audio_bytes, mime="audio/mp3"):
    b64 = base64.b64encode(audio_bytes).decode()
    html = f"""
    <audio autoplay style="width:100%; height:30px; filter: invert(1) hue-rotate(180deg);">
        <source src="data:{mime};base64,{b64}" type="{mime}">
    </audio>
    """
    components.html(html, height=40)

# ---------------- VIEW SWITCH ----------------
is_active = st.session_state.manual_launch

# =========================================
# VIEW 1 – 3D ENTRY SCREEN
# =========================================
if not is_active:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
        <style>
            body {{ margin:0; background:black; overflow:hidden; }}
            #container {{ position:relative; width:100vw; height:100vh; }}
            model-viewer {{ width:100%; height:100%; }}
            #overlay {{
                position:absolute; bottom:80px; left:50%;
                transform:translateX(-50%);
                color:#00FF00; font-size:1.5em;
                text-shadow:0 0 10px #00FF00;
            }}
            #click-layer {{
                position:absolute; top:0; left:0;
                width:100%; height:100%;
                z-index:999; cursor:pointer;
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div id="overlay">[ CLICK_SYSTEM_TO_ACCESS ]</div>
            <div id="click-layer"></div>

            <model-viewer 
                src="{GLB_MODEL_URL}"
                auto-rotate
                rotation-per-second="15deg"
                camera-orbit="0deg 75deg 105%"
                interaction-prompt="none">
            </model-viewer>
        </div>

        <script>
            document.getElementById("click-layer").onclick = () => {{
                window.parent.postMessage("LAUNCH_PLAYER", "*");
            }};
        </script>
    </body>
    </html>
    """
    components.html(html, height=800)

    # Listener to switch Streamlit state
    components.html("""
    <script>
    window.addEventListener("message", (e) => {
        if (e.data === "LAUNCH_PLAYER") {
            window.parent.location.reload();
        }
    });
    </script>
    """, height=0)

    st.session_state.manual_launch = True
    st.stop()

# =========================================
# VIEW 2 – MUSIC PLAYER
# =========================================
else:
    st.markdown("""
    <div class="terminal-header">
        <div>SYSTEM: SHELL_ARCHIVE [SECURE]</div>
        <div>STATUS: <span style="color:#00FF00;">ONLINE</span> <span class="blink">█</span></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.5, 3])

    with c1:
        st.markdown('<div class="close-btn">', unsafe_allow_html=True)
        if st.button("◄ CLOSE"):
            st.session_state.manual_launch = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        icon = "∞ SHUFFLE: ON" if st.session_state.shuffle_mode else "→ SHUFFLE: OFF"
        if st.button(icon):
            st.session_state.shuffle_mode = not st.session_state.shuffle_mode
            if st.session_state.shuffle_mode and playlist:
                st.session_state.current_track = random.choice(playlist)
            st.rerun()

    with c3:
        if st.session_state.current_track:
            track = st.session_state.current_track
            st.markdown(f"**▶ PLAYING:** {track['title']}")
            if track.get("url"):
                audio = fetch_audio_bytes(track["url"])
                if audio:
                    render_custom_player(audio)

    st.markdown('<div class="sheet-container">', unsafe_allow_html=True)

    st.markdown("""
        <div class="sheet-header">
            <div class="cell col-a">#ID</div>
            <div class="cell col-b">TRACK_TITLE</div>
            <div class="cell col-c">ARTIST</div>
            <div class="cell col-d">STATUS</div>
        </div>
    """, unsafe_allow_html=True)

    for i, track in enumerate(playlist):
        is_playing = (st.session_state.current_track == track)
        row_cls = "active-row" if is_playing else ""
        status = "▶ PLAYING" if is_playing else "READY"
        stat_cls = "status-playing" if is_playing else ""

        st.markdown(f'<div class="sheet-row {row_cls}">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1, 6, 3, 2])

        with c1:
            st.markdown(f'<div class="cell col-a" style="border:none;">{i+1:03d}</div>', unsafe_allow_html=True)

        with c2:
            if st.button(f"⟩ {track.get('title','Unknown')}", key=f"btn_{i}"):
                st.session_state.current_track = track
                st.rerun()

        with c3:
            st.markdown(f'<div class="cell col-c" style="border:none;">{track.get("artist","")}</div>', unsafe_allow_html=True)

        with c4:
            st.markdown(f'<div class="cell col-d {stat_cls}" style="border:none;">{status}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
