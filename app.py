import streamlit as st
import json
import requests
from io import BytesIO
import time
import base64
import random

# --- CONFIGURATION ---
# UPDATE THIS TO YOUR ACTUAL DEPLOYED URL
DEPLOY_URL = "https://shellarchive.streamlit.app"

st.set_page_config(
    page_title="SYSTEM_DATA // XLS",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. HOLOGRAPHIC / 3D CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    /* GLOBAL RESET */
    .stApp {
        background-color: #000000;
        color: #00FF00;
        font-family: 'Share Tech Mono', monospace;
        perspective: 1200px; /* THIS CREATES THE 3D SPACE */
        overflow: hidden; /* Hide scrollbars for the immersive feel */
    }
    
    /* HIDE DEFAULT STREAMLIT ELEMENTS */
    header, footer { visibility: hidden; }
    .block-container { 
        padding: 0; 
        max-width: 100%; 
    }

    /* --- THE 3D SCENE CONTAINER --- */
    .scene {
        width: 100%;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        perspective: 1000px;
    }

    /* --- THE FLOATING WORKBOOK OBJECT --- */
    .workbook-3d {
        width: 80%;
        max-width: 1000px;
        height: 70vh;
        background: rgba(0, 10, 0, 0.85);
        border: 2px solid #00FF00;
        box-shadow: 
            0 0 30px rgba(0, 255, 0, 0.2), 
            inset 0 0 50px rgba(0, 0, 0, 0.8);
        
        /* THE 3D TRANSFORM MAGIC */
        transform-style: preserve-3d;
        transform: rotateX(20deg) rotateY(0deg) scale(0.9);
        
        /* ANIMATION */
        animation: float-anim 6s ease-in-out infinite;
        
        overflow-y: auto; /* Internal scrolling */
        position: relative;
        backdrop-filter: blur(4px);
    }
    
    /* SCROLLBAR INSIDE 3D OBJECT */
    .workbook-3d::-webkit-scrollbar { width: 6px; }
    .workbook-3d::-webkit-scrollbar-track { background: #001100; }
    .workbook-3d::-webkit-scrollbar-thumb { background: #00FF00; }

    /* FLOATING ANIMATION */
    @keyframes float-anim {
        0% { transform: rotateX(20deg) translateY(0px); box-shadow: 0 50px 50px rgba(0,0,0,0.5); }
        50% { transform: rotateX(22deg) translateY(-20px); box-shadow: 0 70px 70px rgba(0,0,0,0.6); }
        100% { transform: rotateX(20deg) translateY(0px); box-shadow: 0 50px 50px rgba(0,0,0,0.5); }
    }

    /* --- TERMINAL HEADER (Inside 3D) --- */
    .terminal-header {
        position: sticky;
        top: 0;
        background: #001100;
        border-bottom: 2px solid #00FF00;
        padding: 15px;
        z-index: 10;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }

    /* --- SPREADSHEET ROWS --- */
    .sheet-row {
        display: flex;
        border-bottom: 1px dashed rgba(0, 255, 0, 0.3);
        padding: 8px 0;
        transition: all 0.2s;
        text-decoration: none; /* Remove link underline */
        color: #00FF00;
    }
    .sheet-row:hover {
        background: rgba(0, 255, 0, 0.2);
        transform: translateZ(20px); /* Pop out effect on hover! */
        text-shadow: 0 0 8px #00FF00;
        border-bottom: 1px solid #00FF00;
    }

    .col-id { width: 10%; text-align: center; color: #008800; }
    .col-title { width: 50%; font-weight: bold; }
    .col-artist { width: 25%; color: #00CC00; }
    .col-status { width: 15%; text-align: center; }

    /* --- PLAYER UI --- */
    .player-ui {
        border: 1px solid #00FF00;
        margin: 10px;
        padding: 10px;
        background: rgba(0, 50, 0, 0.3);
        text-align: center;
    }

    /* --- LANDING PAGE --- */
    .file-icon-container {
        position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        perspective: 800px;
    }
    .file-icon {
        font-size: 60px;
        color: #00FF00;
        border: 2px solid #00FF00;
        padding: 40px;
        background: rgba(0,0,0,0.8);
        display: block;
        text-decoration: none;
        animation: spin-intro 10s infinite linear;
    }
    @keyframes spin-intro {
        0% { transform: rotateY(0deg); }
        50% { transform: rotateY(180deg); }
        100% { transform: rotateY(360deg); }
    }
    
    .active-row {
        background: rgba(0, 255, 0, 0.3) !important;
        border-left: 5px solid #00FF00;
    }

    /* SHUFFLE BUTTON */
    .nav-btn {
        display: inline-block;
        border: 1px solid #00FF00;
        padding: 5px 10px;
        color: #00FF00;
        text-decoration: none;
        margin-right: 10px;
        font-size: 0.8em;
    }
    .nav-btn:hover { background: #00FF00; color: black; }
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

# --- CUSTOM AUDIO PLAYER (HIDDEN) ---
def render_custom_player(audio_bytes, mime_type="audio/mp3"):
    """Plays audio and auto-triggers next song on end"""
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
    st.components.v1.html(html_code, height=40)

# --- LOGIC CONTROL ---

# 1. Handle "Next Song" Trigger
if "next_song" in st.query_params:
    if "current_track_index" in st.session_state and playlist:
        current = st.session_state.current_track_index
        if st.session_state.get("shuffle_mode", False):
            next_idx = random.randint(0, len(playlist) - 1)
        else:
            next_idx = (current + 1) % len(playlist)
        st.session_state.current_track_index = next_idx
    # Clean URL
    st.query_params["launched"] = "true"

# 2. Handle "Play Track" Click (From 3D Table)
if "play_index" in st.query_params:
    idx = int(st.query_params["play_index"])
    st.session_state.current_track_index = idx
    # Clean URL but keep launched
    st.query_params["launched"] = "true"

# 3. Handle Shuffle Toggle
if "toggle_shuffle" in st.query_params:
    st.session_state.shuffle_mode = not st.session_state.get("shuffle_mode", False)
    st.query_params["launched"] = "true"

# 4. Handle Close
if "close_file" in st.query_params:
    st.session_state.manual_launch = False
    st.session_state.current_track_index = None
    st.query_params.clear()

# Initialize Defaults
if 'manual_launch' not in st.session_state: st.session_state.manual_launch = False
if 'current_track_index' not in st.session_state: st.session_state.current_track_index = None
if 'shuffle_mode' not in st.session_state: st.session_state.shuffle_mode = False

# Determine Activity
query_params = st.query_params
url_launched = query_params.get("launched") == "true"
is_active = url_launched or st.session_state.manual_launch


# ==========================================
# VIEW 1: LANDING PAGE (3D CUBE ICON)
# ==========================================
if not is_active:
    st.markdown(f"""
        <div class="file-icon-container">
            <a href="{DEPLOY_URL}/?launched=true" target="_top" class="file-icon">
                [XLS]
            </a>
            <div class="file-label">SYSTEM_WORKBOOK</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# VIEW 2: THE 3D INTERACTIVE SPREADSHEET
# ==========================================
else:
    # Prepare Player Data
    current_track = None
    if st.session_state.current_track_index is not None:
        current_track = playlist[st.session_state.current_track_index]

    # --- BUILD THE HTML STRING FOR THE 3D OBJECT ---
    # We build one massive HTML string to inject into the 3D container
    
    # Header Section
    shuffle_status = "ON" if st.session_state.shuffle_mode else "OFF"
    shuffle_link = f"{DEPLOY_URL}/?toggle_shuffle=true&launched=true"
    close_link = f"{DEPLOY_URL}/?close_file=true"
    
    html_content = f"""
    <div class="scene">
        <div class="workbook-3d">
            
            <div class="terminal-header">
                <div style="display:flex; justify-content:space-between;">
                    <span>SYSTEM: WORKBOOK_INTERFACE_3D</span>
                    <span>{time.strftime('%H:%M:%S')}</span>
                </div>
                <div style="margin-top:10px;">
                    <a href="{close_link}" target="_top" class="nav-btn">◄ CLOSE</a>
                    <a href="{shuffle_link}" target="_top" class="nav-btn">∞ SHUFFLE: {shuffle_status}</a>
                </div>
    """

    # Player Section (if playing)
    if current_track:
        html_content += f"""
            <div class="player-ui">
                <div>▶ NOW_PLAYING: {current_track['title']}</div>
                <div style="font-size:0.8em; opacity:0.8;">{current_track['artist']}</div>
            </div>
        """
    
    html_content += "</div>" # End Header

    # Table Header
    html_content += """
            <div style="padding:10px; border-bottom:2px double #00FF00; display:flex; font-weight:bold;">
                <div class="col-id">#</div>
                <div class="col-title">TRACK_TITLE</div>
                <div class="col-artist">ARTIST</div>
                <div class="col-status">STATUS</div>
            </div>
    """

    # Table Rows
    for i, track in enumerate(playlist):
        is_playing = (i == st.session_state.current_track_index)
        row_active = "active-row" if is_playing else ""
        status = "PLAYING" if is_playing else "LOAD"
        
        # LINK: Clicking a row reloads page with ?play_index=i
        play_link = f"{DEPLOY_URL}/?play_index={i}&launched=true"
        
        html_content += f"""
            <a href="{play_link}" target="_top" class="sheet-row {row_active}">
                <div class="col-id">{i+1:03}</div>
                <div class="col-title">{track['title']}</div>
                <div class="col-artist">{track['artist']}</div>
                <div class="col-status">[{status}]</div>
            </a>
        """

    html_content += """
            <div style="padding:20px; text-align:center; opacity:0.5;">/// END OF FILE ///</div>
        </div> </div> """

    # RENDER THE 3D OBJECT
    st.markdown(html_content, unsafe_allow_html=True)

    # RENDER AUDIO PLAYER (Invisible)
    if current_track and current_track.get('url'):
        audio_data = fetch_audio_bytes(current_track['url'])
        if audio_data:
            render_custom_player(audio_data)
