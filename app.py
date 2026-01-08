import streamlit as st
import json
import requests
from io import BytesIO
import time

# --- CONFIGURATION ---
DEPLOY_URL = "https://shellarchive.streamlit.app"

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
    
    /* SCANLINES EFFECT */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            rgba(18, 16, 16, 0) 50%, 
            rgba(0, 0, 0, 0.25) 50%
        );
        background-size: 100% 4px;
        pointer-events: none;
        z-index: 9999;
        animation: scanlines 0.1s linear infinite;
    }
    
    @keyframes scanlines {
        0% { background-position: 0 0; }
        100% { background-position: 0 4px; }
    }
    
    /* CRT GLOW */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(ellipse at center, rgba(0,255,0,0.1) 0%, transparent 70%);
        pointer-events: none;
        z-index: 9998;
    }
    
    /* REMOVE PADDING */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
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
        box-shadow: 
            0 0 20px rgba(0, 255, 0, 0.3),
            inset 0 0 20px rgba(0, 255, 0, 0.1);
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
    }
    .file-icon:hover {
        background: rgba(0, 255, 0, 0.1);
        box-shadow: 
            0 0 50px rgba(0, 255, 0, 0.8),
            inset 0 0 30px rgba(0, 255, 0, 0.2);
        transform: scale(1.05);
    }
    .file-label {
        margin-top: 20px;
        display: block;
        letter-spacing: 3px;
        font-size: 1.3em;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
    }

    /* --- TERMINAL HEADER --- */
    .terminal-header {
        border: 2px solid #00FF00;
        padding: 15px;
        margin-bottom: 10px;
        background: rgba(0, 20, 0, 0.5);
        box-shadow: 
            0 0 10px rgba(0, 255, 0, 0.3),
            inset 0 0 10px rgba(0, 0, 0, 0.5);
        font-size: 0.9em;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
    }
    
    .blink {
        animation: blink 1s step-start infinite;
    }
    
    @keyframes blink {
        50% { opacity: 0; }
    }

    /* --- SPREADSHEET GRID --- */
    .sheet-container {
        border: 3px double #00FF00;
        margin-top: 20px;
        background: rgba(0, 10, 0, 0.3);
        box-shadow: 
            0 0 20px rgba(0, 255, 0, 0.2),
            inset 0 0 20px rgba(0, 0, 0, 0.5);
    }

    /* Header Row */
    .sheet-header {
        display: flex;
        border-bottom: 3px double #00FF00;
        background: rgba(0, 50, 0, 0.4);
        padding: 12px 0;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 8px rgba(0, 255, 0, 0.8);
    }

    /* Data Rows */
    .sheet-row {
        display: flex;
        border-bottom: 1px solid #00FF00;
        align-items: center;
        transition: all 0.2s;
        min-height: 40px;
    }
    .sheet-row:hover {
        background: rgba(0, 255, 0, 0.08);
        box-shadow: inset 0 0 10px rgba(0, 255, 0, 0.1);
    }

    /* Columns */
    .col-a { 
        width: 8%; 
        border-right: 1px solid #00FF00; 
        padding: 10px; 
        text-align: center;
        font-weight: bold;
        color: #00AA00;
    }
    .col-b { 
        width: 50%; 
        border-right: 1px solid #00FF00; 
        padding: 10px;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
    }
    .col-c { 
        width: 22%; 
        border-right: 1px solid #00FF00; 
        padding: 10px;
        color: #00DD00;
    }
    .col-d { 
        width: 20%; 
        padding: 10px; 
        text-align: center;
        font-weight: bold;
    }

    /* Button Styling */
    .stButton > button {
        border: none;
        background: transparent;
        color: #00FF00;
        text-align: left;
        padding: 0;
        margin: 0;
        font-family: 'Share Tech Mono', monospace;
        text-transform: uppercase;
        width: 100%;
        cursor: pointer;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
        transition: all 0.2s;
    }
    .stButton > button:hover {
        color: #FFFFFF;
        background: rgba(0, 255, 0, 0.1);
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
        letter-spacing: 1px;
    }
    
    /* Active Row Highlight */
    .active-row {
        background: rgba(0, 255, 0, 0.15) !important;
        box-shadow: inset 0 0 15px rgba(0, 255, 0, 0.3);
        border-left: 4px solid #00FF00;
    }
    
    /* Player Container */
    .player-container {
        border: 2px solid #00FF00;
        padding: 12px;
        background: rgba(0, 30, 0, 0.5);
        margin-bottom: 10px;
        box-shadow: 
            0 0 15px rgba(0, 255, 0, 0.2),
            inset 0 0 10px rgba(0, 0, 0, 0.5);
    }
    
    /* Close Button */
    .close-btn {
        background: transparent !important;
        border: 2px solid #00FF00 !important;
        color: #00FF00 !important;
        padding: 8px 20px !important;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.5) !important;
        transition: all 0.3s !important;
    }
    .close-btn:hover {
        background: rgba(0, 255, 0, 0.2) !important;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.5) !important;
    }
    
    /* Audio Player Styling */
    audio {
        filter: hue-rotate(90deg) brightness(1.2);
    }
    
    /* Glitch Text Effect */
    .glitch {
        position: relative;
        animation: glitch-skew 2s infinite;
    }
    
    @keyframes glitch-skew {
        0% { transform: skew(0deg); }
        10% { transform: skew(-2deg); }
        20% { transform: skew(2deg); }
        30% { transform: skew(0deg); }
        100% { transform: skew(0deg); }
    }
    
    /* Status Indicators */
    .status-ready {
        color: #00AA00;
        text-shadow: 0 0 5px rgba(0, 170, 0, 0.5);
    }
    .status-playing {
        color: #00FF00;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA & PROXY LOGIC ---
@st.cache_data
def load_secure_playlist():
    """Loads secure data from secrets.toml"""
    try:
        if "PLAYLIST_DATA" in st.secrets:
            return json.loads(st.secrets["PLAYLIST_DATA"])
        else:
            return [{"title": "ERROR", "artist": "NO DATA", "url": ""}]
    except Exception:
        return []

@st.cache_data(show_spinner=False)
def fetch_audio_bytes(url):
    """Secure Proxy: Server downloads file, passes bytes to browser."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content
    except Exception:
        return None

playlist = load_secure_playlist()

# --- STATE MANAGEMENT ---
query_params = st.query_params
url_launched = query_params.get("launched") == "true"
if 'manual_launch' not in st.session_state:
    st.session_state.manual_launch = False

is_active = url_launched or st.session_state.manual_launch

if 'current_track' not in st.session_state:
    st.session_state.current_track = None

# ==========================================
# VIEW 1: THE LANDING PAGE
# ==========================================
if not is_active:
    st.markdown(f"""
        <div class="file-icon-container">
            <a href="{DEPLOY_URL}/?launched=true" target="_top" class="file-icon">
                <div class="glitch">[XLS]</div>
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
        <div>SYSTEM: WORKBOOK_INTERFACE v2.1.9</div>
        <div>SESSION: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        <div>STATUS: <span style="color:#00FF00;">CONNECTED</span> <span class="blink">█</span></div>
        <div>RECORDS_LOADED: {len(playlist):03d}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Top Navigation ---
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("◄◄ CLOSE_FILE", key="close", help="Exit workbook"):
            st.session_state.manual_launch = False
            st.query_params.clear()
            st.rerun()

    with col2:
        if st.session_state.current_track:
            track = st.session_state.current_track
            st.markdown(f"""
            <div class="player-container">
                <div style="color:#00FF00; font-weight:bold; margin-bottom:5px;">
                    ▶ NOW_PROCESSING: {track['title']} // {track['artist']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if track.get('url'):
                audio_data = fetch_audio_bytes(track['url'])
                if audio_data:
                    st.audio(BytesIO(audio_data), format="audio/mp3", autoplay=True)
                else:
                    st.error("⚠ ERR_CONNECTION_REFUSED")

    # --- Spreadsheet Header ---
    st.markdown("""
    <div class="sheet-container">
        <div class="sheet-header">
            <div class="col-a">#ID</div>
            <div class="col-b">TRACK_TITLE [CLICK_TO_EXECUTE]</div>
            <div class="col-c">ARTIST_REFERENCE</div>
            <div class="col-d">STATUS</div>
        </div>
    """, unsafe_allow_html=True)

    # --- Spreadsheet Rows ---
    for i, track in enumerate(playlist):
        is_playing = (st.session_state.current_track == track)
        row_class = "active-row" if is_playing else ""
        status_class = "status-playing" if is_playing else "status-ready"
        status_text = "▶ PLAY" if is_playing else "READY"
        
        # Create row container
        st.markdown(f'<div class="sheet-row {row_class}">', unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns([1, 6.5, 2.8, 2.5])
        
        with c1:
            st.markdown(f"<div class='col-a'>{i+1:03d}</div>", unsafe_allow_html=True)
        
        with c2:
            if st.button(f"⟩ {track.get('title', 'Unknown')}", key=f"btn_{i}"):
                st.session_state.current_track = track
                st.rerun()
        
        with c3:
            st.markdown(f"<div class='col-c'>{track.get('artist', 'Unknown')}</div>", unsafe_allow_html=True)

        with c4:
            st.markdown(f"<div class='col-d {status_class}'>{status_text}</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Footer Info ---
    st.markdown(f"""
    <div class="terminal-header" style="margin-top:20px; font-size:0.8em;">
        <div>END_OF_WORKBOOK // TOTAL_ENTRIES: {len(playlist)} // MEMORY_USAGE: OK</div>
    </div>
    """, unsafe_allow_html=True)
