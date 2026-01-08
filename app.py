import streamlit as st
import streamlit.components.v1 as components  # <--- THIS WAS MISSING
import json
import requests
from io import BytesIO
import time
import base64
import random

# --- CONFIGURATION ---
# UPDATE THIS TO YOUR ACTUAL URL
DEPLOY_URL = "https://shellarchive.streamlit.app" 

# REPLACE THIS WITH YOUR OWN GLB FILE IF YOU HAVE ONE
# For now, I'm using a placeholder "Sci-Fi Tablet" from a public CDN
GLB_MODEL_URL = "https://github.com/kevfromglasgow/shellarchive/blob/main/shell.glb" 

st.set_page_config(
    page_title="SYSTEM_DATA // XLS",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. CSS: RETRO & 3D STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    /* GLOBAL RESET */
    .stApp {
        background-color: #000000;
        color: #00FF00;
        font-family: 'Share Tech Mono', monospace;
    }
    
    /* REMOVE PADDING */
    .block-container { 
        padding-top: 0; 
        padding-bottom: 0; 
        max-width: 100%; 
    }
    header, footer { visibility: hidden; }

    /* --- 3D CONTAINER (IDLE STATE) --- */
    .scene-3d {
        width: 100%;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        background: radial-gradient(circle at center, #001100 0%, #000000 70%);
    }

    /* --- WORKBOOK CONTAINER (ACTIVE STATE) --- */
    .workbook-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 40px;
        animation: slide-up 0.5s ease-out;
    }
    @keyframes slide-up {
        from { transform: translateY(50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    /* --- TERMINAL HEADER --- */
    .terminal-header {
        border: 2px solid #00FF00;
        padding: 15px;
        margin-bottom: 20px;
        background: rgba(0, 20, 0, 0.8);
        font-size: 0.9em;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.1);
    }
    .blink { animation: blink 1s step-start infinite; }
    @keyframes blink { 50% { opacity: 0; } }

    /* --- SPREADSHEET GRID --- */
    .sheet-container {
        border: 2px solid #00FF00;
        background: rgba(0, 10, 0, 0.9);
        box-shadow: 0 0 30px rgba(0, 255, 0, 0.1);
    }
    .sheet-header {
        display: flex;
        align-items: center;
        border-bottom: 2px double #00FF00;
        background: rgba(0, 50, 0, 0.6);
        padding: 12px 0;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .sheet-row {
        border-bottom: 1px solid #003300;
        min-height: 45px;
        display: flex;
        align-items: stretch;
        transition: 0.2s;
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
    
    .col-a { border-right: 1px solid #00FF00; color: #00AA00; justify-content: center; height: 100%; }
    .col-b { border-right: 1px solid #00FF00; height: 100%; width: 100%; }
    .col-c { border-right: 1px solid #00FF00; color: #00DD00; height: 100%; }
    .col-d { justify-content: center; font-weight: bold; height: 100%; }

    /* Button Styling */
    .stButton { width: 100%; height: 100%; margin: 0; }
    .stButton > button {
        border: none;
        background: transparent;
        color: #00FF00;
        text-align: left;
        padding: 8px 0;
        margin: 0;
        font-family: 'Share Tech Mono', monospace;
        text-transform: uppercase;
        width: 100%;
        height: 100%;
        line-height: 1.2;
    }
    .stButton > button:hover {
        color: #FFFFFF;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
    }
    
    .active-row {
        background: rgba(0, 255, 0, 0.2) !important;
        border-left: 4px solid #00FF00;
    }
    
    .status-playing { 
        color: #00FF00; 
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
        animation: pulse 1.5s infinite; 
    }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }

    /* CLOSE BUTTON */
    .close-btn button {
        border: 1px solid #00FF00 !important;
        color: #00FF00 !important;
    }
    .close-btn button:hover {
        background: #00FF00 !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA & PROXY LOGIC ---
@st.cache_data
def load_secure_playlist():
    try:
        if "PLAYLIST_DATA" in st.secrets:
            return json.loads(st.secrets["PLAYLIST_DATA"])
        else:
            return [{"title": "ERROR", "artist": "NO DATA", "url": ""}]
    except Exception:
        return []

@st.cache_data(show_spinner=False)
def fetch_audio_bytes(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content
    except Exception:
        return None

playlist = load_secure_playlist()

# --- CUSTOM AUDIO PLAYER ---
def render_custom_player(audio_bytes, mime_type="audio/mp3"):
    b64_audio = base64.b64encode(audio_bytes).decode()
    next_link = f"{DEPLOY_URL}/?next_song=true&launched=true"
    
    html_code = f"""
    <audio id="custom-player" autoplay style="width:100%; height:30px; filter: invert(1) hue-rotate(180deg);">
        <source src="data:{mime_type};base64,{b64_audio}" type="{mime_type}">
    </audio>
    <a id="auto-next-link" href="{next_link}" target="_top" style="display:none;">NEXT</a>
    <script>
        const player = document.getElementById('custom-player');
        player.volume = 0.8;
        player.onended = function() {{
            document.getElementById('auto-next-link').click();
        }};
    </script>
    """
    components.html(html_code, height=40)

# --- STATE MANAGEMENT ---
if "next_song" in st.query_params:
    st.query_params.clear()
    if "current_track" in st.session_state and playlist:
        try:
            current_idx = playlist.index(st.session_state.current_track)
        except ValueError:
            current_idx = 0
        
        if st.session_state.get("shuffle_mode", False):
            next_idx = random.randint(0, len(playlist) - 1)
        else:
            next_idx = (current_idx + 1) % len(playlist)
            
        st.session_state.current_track = playlist[next_idx]
    st.query_params["launched"] = "true"

query_params = st.query_params
url_launched = query_params.get("launched") == "true"
if 'manual_launch' not in st.session_state:
    st.session_state.manual_launch = False

is_active = url_launched or st.session_state.manual_launch

if 'current_track' not in st.session_state:
    st.session_state.current_track = None

if 'shuffle_mode' not in st.session_state:
    st.session_state.shuffle_mode = False

# ==========================================
# VIEW 1: THE 3D MODEL VIEWER (IDLE STATE)
# ==========================================
if not is_active:
    # 1. We construct the Link URL for Python
    target_link = f"{DEPLOY_URL}/?launched=true"
    
    # 2. Render the Model Viewer
    # The user can Rotate/Zoom the model.
    # Clicking it triggers the link to open the workbook.
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
        <style>
            body {{ margin: 0; background: black; overflow: hidden; font-family: 'Courier New', monospace; }}
            model-viewer {{ width: 100vw; height: 100vh; --poster-color: transparent; }}
            
            /* INSTRUCTION OVERLAY */
            #overlay {{
                position: absolute; bottom: 50px; left: 50%; transform: translateX(-50%);
                color: #00FF00; font-size: 1.2em; letter-spacing: 2px;
                text-align: center; pointer-events: none;
                text-shadow: 0 0 10px #00FF00;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}

            /* HIDDEN LINK OVERLAY */
            /* We make a transparent link cover the model so clicking ANYWHERE works */
            #click-trigger {{
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                z-index: 999; cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div id="overlay">
            [ CLICK_TO_ACCESS_DATA ]
        </div>

        <a id="click-trigger" href="{target_link}" target="_top"></a>

        <model-viewer 
            src="{GLB_MODEL_URL}"
            camera-controls 
            auto-rotate 
            rotation-per-second="10deg"
            shadow-intensity="1" 
            exposure="0.7"
            camera-orbit="0deg 75deg 105%" 
            interaction-prompt="none">
        </model-viewer>
    </body>
    </html>
    """
    components.html(html_code, height=800)


# ==========================================
# VIEW 2: THE INTERACTIVE WORKBOOK (ACTIVE)
# ==========================================
else:
    # Container for the "Real" App
    st.markdown('<div class="workbook-container">', unsafe_allow_html=True)
    
    # --- Terminal Header ---
    st.markdown(f"""
    <div class="terminal-header">
        <div>SYSTEM: WORKBOOK_INTERFACE [SECURE_CONNECTION]</div>
        <div>SESSION: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        <div>STATUS: <span style="color:#00FF00;">ONLINE</span> <span class="blink">█</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Controls ---
    c1, c2, c3 = st.columns([1, 1.5, 3])
    
    with c1:
        st.markdown('<div class="close-btn">', unsafe_allow_html=True)
        if st.button("◄ CLOSE", key="close"):
            st.session_state.manual_launch = False
            st.query_params.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        shuffle_txt = "∞ SHUFFLE: ON" if st.session_state.shuffle_mode else "→ SHUFFLE: OFF"
        if st.button(shuffle_txt, key="shuffle"):
            st.session_state.shuffle_mode = not st.session_state.shuffle_mode
            if st.session_state.shuffle_mode and playlist:
                st.session_state.current_track = random.choice(playlist)
            st.rerun()

    with c3:
        if st.session_state.current_track:
            track = st.session_state.current_track
            st.markdown(f"**▶ PLAYING:** {track['title']}")
            
            if track.get('url'):
                audio_data = fetch_audio_bytes(track['url'])
                if audio_data:
                    render_custom_player(audio_data)
                else:
                    st.error("ERR_LOAD")

    # --- Spreadsheet ---
    st.markdown('<div class="sheet-container">', unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="sheet-header" style="display: flex;">
            <div class="cell col-a" style="flex: 1;">#ID</div>
            <div class="cell col-b" style="flex: 6;">TRACK_TITLE</div>
            <div class="cell col-c" style="flex: 3;">ARTIST_REF</div>
            <div class="cell col-d" style="flex: 2;">STATUS</div>
        </div>
    """, unsafe_allow_html=True)

    # Rows
    for i, track in enumerate(playlist):
        is_playing = (st.session_state.current_track == track)
        row_class = "active-row" if is_playing else ""
        status_text = "▶ EXECUTE" if is_playing else "READY"
        status_class = "status-playing" if is_playing else ""
        
        st.markdown(f'<div class="sheet-row {row_class}">', unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns([1, 6, 3, 2])
        
        with c1:
            st.markdown(f'<div class="cell col-a" style="height:100%; border:none;">{i+1:03d}</div>', unsafe_allow_html=True)
        
        with c2:
            if st.button(f"⟩ {track.get('title', 'Unknown')}", key=f"btn_{i}"):
                st.session_state.current_track = track
                st.rerun()
        
        with c3:
            st.markdown(f'<div class="cell col-c" style="height:100%; border:none;">{track.get('artist', 'Unknown')}</div>', unsafe_allow_html=True)

        with c4:
            st.markdown(f'<div class="cell col-d {status_class}" style="height:100%; border:none;">{status_text}</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # End Sheet
    st.markdown('</div>', unsafe_allow_html=True) # End Container
