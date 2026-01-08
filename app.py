import streamlit as st
import json
import requests
from io import BytesIO
import time
import base64
import random

# --- CONFIGURATION ---
# UPDATE THIS TO YOUR ACTUAL DEPLOYED URL
DEPLOY_URL = "https://shellarchive.streamlit.app/?launched=true"

st.set_page_config(
    page_title="SYSTEM_DATA // XLS",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ENHANCED RETRO TERMINAL CSS ---
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
        padding-top: 1rem; 
        padding-bottom: 5rem; 
        max-width: 95% !important; 
    }
    header, footer { visibility: hidden; }

    /* --- LANDING PAGE ICON --- */
    .file-icon-container {
        position: fixed;
        top: 50vh;
        left: 50vw;
        transform: translate(-50%, -50%);
        text-align: center;
        z-index: 10;
    }
    .file-icon {
        font-size: 80px;
        color: #00FF00;
        text-decoration: none;
        border: 3px solid #00FF00;
        padding: 50px 60px;
        display: block;
        transition: all 0.3s;
        background: rgba(0, 0, 0, 0.9);
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
    }
    .file-icon:hover {
        background: rgba(0, 255, 0, 0.1);
        box-shadow: 0 0 50px rgba(0, 255, 0, 0.8);
        transform: scale(1.05);
    }
    .file-label {
        margin-top: 20px;
        display: block;
        letter-spacing: 3px;
        font-size: 0.3em; 
    }

    /* --- TERMINAL HEADER --- */
    .terminal-header {
        border: 2px solid #00FF00;
        padding: 15px;
        margin-bottom: 20px;
        background: rgba(0, 20, 0, 0.5);
        font-size: 0.9em;
    }
    .blink { animation: blink 1s step-start infinite; }
    @keyframes blink { 50% { opacity: 0; } }

    /* --- SPREADSHEET GRID --- */
    .sheet-container {
        border: 3px double #00FF00;
        background: rgba(0, 10, 0, 0.3);
    }
    .sheet-header {
        display: flex;
        align-items: center;
        border-bottom: 3px double #00FF00;
        background: rgba(0, 50, 0, 0.4);
        padding: 10px 0;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .sheet-row {
        border-bottom: 1px solid #00FF00;
        min-height: 45px;
        display: flex;
        align-items: stretch;
    }
    .sheet-row:hover {
        background: rgba(0, 255, 0, 0.08);
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
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis; 
    }
    .stButton > button:hover {
        color: #FFFFFF;
        background: transparent;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
    }
    
    .active-row {
        background: rgba(0, 255, 0, 0.15) !important;
        border-left: 4px solid #00FF00;
    }
    
    .player-container {
        border: 2px solid #00FF00;
        padding: 10px;
        background: rgba(0, 30, 0, 0.5);
        margin-bottom: 20px;
    }
    
    .status-ready { color: #00AA00; }
    .status-playing { 
        color: #00FF00; 
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
        animation: pulse 1.5s infinite; 
    }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
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

# --- HELPER: CUSTOM HTML PLAYER WITH AUTO-NEXT ---
def render_custom_player(audio_bytes, mime_type="audio/mp3"):
    """
    Renders an HTML5 audio player that:
    1. Plays secure bytes (no URL leak)
    2. Detects 'ended' event
    3. Clicks a hidden link to ?next_song=true to trigger Python logic
    """
    b64_audio = base64.b64encode(audio_bytes).decode()
    
    # We create a hidden link that points to the DEPLOY_URL with a query param
    # target="_top" ensures it reloads the main window, not the iframe
    next_link = f"{DEPLOY_URL}/?next_song=true"
    
    html_code = f"""
    <style>
        audio {{ width: 100%; filter: invert(100%); margin-top: 5px; }}
    </style>
    
    <audio id="custom-player" controls autoplay>
        <source src="data:{mime_type};base64,{b64_audio}" type="{mime_type}">
    </audio>
    
    <a id="auto-next-link" href="{next_link}" target="_top" style="display:none;">NEXT</a>

    <script>
        const player = document.getElementById('custom-player');
        player.onended = function() {{
            // When audio finishes, click the hidden link to reload page with next song
            document.getElementById('auto-next-link').click();
        }};
    </script>
    """
    # Height must be enough to show the controls
    st.components.v1.html(html_code, height=60)


# --- STATE MANAGEMENT ---
# 1. Handle "Next Song" Trigger (from auto-play)
if "next_song" in st.query_params:
    # Clear the param so we don't loop forever
    st.query_params.clear()
    
    if "current_track" in st.session_state and playlist:
        # Find current index
        try:
            current_idx = playlist.index(st.session_state.current_track)
        except ValueError:
            current_idx = 0
            
        # Determine Next Index
        if st.session_state.get("shuffle_mode", False):
            next_idx = random.randint(0, len(playlist) - 1)
        else:
            next_idx = (current_idx + 1) % len(playlist)
            
        st.session_state.current_track = playlist[next_idx]

# 2. Check Launch State
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
# VIEW 1: THE LANDING PAGE
# ==========================================
if not is_active:
    st.markdown(f"""
        <div class="file-icon-container">
            <a href="{DEPLOY_URL}/?launched=true" target="_top" class="file-icon">
                [XLS]
                <span class="file-label">ACCESS_WORKBOOK.XLS</span>
            </a>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# VIEW 2: THE INTERACTIVE SPREADSHEET
# ==========================================
else:
    # --- Terminal Header ---
    st.markdown(f"""
    <div class="terminal-header">
        <div>SYSTEM: WORKBOOK_INTERFACE v3.0 [AUTO_SEQ]</div>
        <div>SESSION: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        <div>STATUS: <span style="color:#00FF00;">CONNECTED</span> <span class="blink">█</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Top Navigation & Controls ---
    col1, col2, col3 = st.columns([1.5, 1.5, 4])
    
    with col1:
        if st.button("◄◄ CLOSE_FILE", key="close"):
            st.session_state.manual_launch = False
            st.query_params.clear()
            st.rerun()

    with col2:
        # SHUFFLE BUTTON
        shuffle_icon = "∞ SHUFFLE: ON" if st.session_state.shuffle_mode else "→ SHUFFLE: OFF"
        if st.button(shuffle_icon, key="shuffle"):
            st.session_state.shuffle_mode = not st.session_state.shuffle_mode
            # If turning ON, pick a random track immediately
            if st.session_state.shuffle_mode and playlist:
                st.session_state.current_track = random.choice(playlist)
            st.rerun()

    with col3:
        if st.session_state.current_track:
            track = st.session_state.current_track
            st.markdown(f"""
            <div class="player-container">
                <div style="color:#00FF00; font-weight:bold; margin-bottom:0px;">
                    ▶ NOW_PROCESSING: {track['title']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- CUSTOM PLAYER LOGIC ---
            if track.get('url'):
                audio_data = fetch_audio_bytes(track['url'])
                if audio_data:
                    # Use custom player instead of st.audio to handle auto-next
                    render_custom_player(audio_data)
                else:
                    st.error("⚠ ERR_CONNECTION_REFUSED")

    # --- SPREADSHEET ---
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
        status_text = "▶ PLAYING" if is_playing else "READY"
        status_class = "status-playing" if is_playing else "status-ready"
        
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

    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="terminal-header" style="margin-top:20px; font-size:0.8em; text-align:right;">
        MODE: {'SHUFFLE' if st.session_state.shuffle_mode else 'SEQUENTIAL'} // ENTRIES: {len(playlist)}
    </div>
    """, unsafe_allow_html=True)
