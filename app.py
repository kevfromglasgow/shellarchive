import streamlit as st
import json
import requests
from io import BytesIO
import time

# --- CONFIGURATION ---
DEPLOY_URL = "https://shellarchive.streamlit.app"

st.set_page_config(
    page_title="VISICALC - AUDIO EDITION",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- VISICALC-INSPIRED CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    /* GLOBAL - VisiCalc used white/amber on black */
    .stApp {
        background-color: #000000;
        color: #FFB000;
        font-family: 'VT323', monospace;
        font-size: 18px;
        line-height: 1.2;
    }
    
    /* REMOVE PADDING */
    .block-container { 
        padding-top: 0.5rem; 
        padding-bottom: 0.5rem;
        max-width: 100%;
    }
    header, footer { visibility: hidden; }

    /* --- LANDING PAGE --- */
    .file-icon-container {
        position: fixed;
        top: 50vh;
        left: 50vw;
        transform: translate(-50%, -50%);
        text-align: center;
        z-index: 10;
    }
    .file-icon {
        font-size: 60px;
        color: #FFB000;
        text-decoration: none;
        border: 2px solid #FFB000;
        padding: 40px 50px;
        display: block;
        transition: all 0.2s;
        background: #000000;
        font-family: 'VT323', monospace;
    }
    .file-icon:hover {
        background: #FFB000;
        color: #000000;
    }
    .file-label {
        margin-top: 15px;
        display: block;
        letter-spacing: 2px;
        font-size: 1.1em;
    }

    /* --- VISICALC STATUS BAR (Top) --- */
    .status-bar {
        background: #000000;
        border: 1px solid #FFB000;
        padding: 8px 15px;
        margin-bottom: 3px;
        font-family: 'VT323', monospace;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #FFB000;
    }
    
    .status-left {
        display: flex;
        gap: 30px;
    }
    
    .cell-ref {
        font-weight: bold;
        color: #FFFFFF;
    }

    /* --- COMMAND BAR (VisiCalc had a prompt line) --- */
    .command-bar {
        background: #000000;
        border: 1px solid #FFB000;
        border-top: none;
        padding: 5px 15px;
        margin-bottom: 3px;
        font-family: 'VT323', monospace;
        color: #FFFFFF;
    }

    /* --- SPREADSHEET GRID --- */
    .sheet-container {
        border: 1px solid #FFB000;
        margin-top: 5px;
        background: #000000;
    }

    /* Column Headers (A, B, C...) */
    .column-headers {
        display: flex;
        border-bottom: 1px solid #FFB000;
        background: #000000;
    }
    
    .col-header {
        text-align: center;
        padding: 5px;
        border-right: 1px solid #FFB000;
        color: #FFB000;
        font-weight: bold;
    }

    /* Data Rows */
    .sheet-row {
        display: flex;
        border-bottom: 1px solid #333333;
        align-items: stretch;
        min-height: 28px;
        background: #000000;
    }
    
    .sheet-row:hover {
        background: #1a1a00;
    }

    /* Row number */
    .row-num {
        width: 50px;
        border-right: 1px solid #FFB000;
        padding: 5px;
        text-align: right;
        color: #FFB000;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }

    /* Columns */
    .cell {
        padding: 5px 8px;
        border-right: 1px solid #333333;
        display: flex;
        align-items: center;
        color: #FFB000;
    }
    
    .cell-a { width: 80px; justify-content: center; font-weight: bold; }
    .cell-b { width: 400px; }
    .cell-c { width: 250px; }
    .cell-d { width: 120px; justify-content: center; }

    /* Button Styling - VisiCalc style */
    .stButton > button {
        border: none;
        background: transparent;
        color: #FFB000;
        text-align: left;
        padding: 0;
        margin: 0;
        font-family: 'VT323', monospace;
        font-size: 18px;
        width: 100%;
        cursor: pointer;
        transition: color 0.1s;
    }
    .stButton > button:hover {
        color: #FFFFFF;
        background: transparent;
    }
    
    /* Active/Selected Row */
    .active-row {
        background: #2a2200 !important;
    }
    
    .active-row .cell {
        color: #FFFFFF;
    }

    /* Close Button */
    .close-btn-container {
        margin-bottom: 5px;
    }
    
    /* Player */
    .player-box {
        border: 1px solid #FFB000;
        padding: 8px 15px;
        margin-bottom: 5px;
        background: #000000;
        color: #FFFFFF;
    }
    
    /* Bottom info bar */
    .bottom-bar {
        border: 1px solid #FFB000;
        border-top: none;
        padding: 5px 15px;
        margin-top: -1px;
        background: #000000;
        color: #FFB000;
        text-align: center;
    }
    
    /* Hide default streamlit elements */
    .stButton button:focus {
        outline: none;
        box-shadow: none;
    }
    
    /* Audio player styling */
    audio {
        width: 100%;
        height: 30px;
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
# VIEW 1: LANDING PAGE
# ==========================================
if not is_active:
    st.markdown(f"""
        <div class="file-icon-container">
            <a href="{DEPLOY_URL}/?launched=true" target="_top" class="file-icon">
                VISICALC
                <span class="file-label">AUDIO EDITION</span>
            </a>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# VIEW 2: VISICALC SPREADSHEET
# ==========================================
else:
    # Get current track info for status bar
    current_cell = "A1"
    current_value = ""
    if st.session_state.current_track:
        for i, track in enumerate(playlist):
            if track == st.session_state.current_track:
                current_cell = f"B{i+1}"
                current_value = f'"{track["title"]}"'
                break
    
    # --- STATUS BAR (VisiCalc-style) ---
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-left">
            <span class="cell-ref">{current_cell}</span>
            <span>{current_value}</span>
        </div>
        <div>MEMORY: {len(playlist)} TRACKS LOADED</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- COMMAND BAR ---
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("/Q - QUIT", key="close"):
            st.session_state.manual_launch = False
            st.query_params.clear()
            st.rerun()
    
    with col2:
        if st.session_state.current_track:
            track = st.session_state.current_track
            st.markdown(f"""
            <div class="player-box">
                NOW PLAYING: {track['title']} - {track['artist']}
            </div>
            """, unsafe_allow_html=True)
            
            if track.get('url'):
                audio_data = fetch_audio_bytes(track['url'])
                if audio_data:
                    st.audio(BytesIO(audio_data), format="audio/mp3", autoplay=True)
                else:
                    st.error("ERROR: CONNECTION FAILED")

    # --- SPREADSHEET GRID ---
    st.markdown("""
    <div class="sheet-container">
        <!-- Column Headers -->
        <div class="column-headers">
            <div class="row-num"></div>
            <div class="col-header" style="width:80px;">A</div>
            <div class="col-header" style="width:400px;">B</div>
            <div class="col-header" style="width:250px;">C</div>
            <div class="col-header" style="width:120px; border-right:none;">D</div>
        </div>
    """, unsafe_allow_html=True)

    # --- Data Rows ---
    for i, track in enumerate(playlist):
        is_playing = (st.session_state.current_track == track)
        row_class = "active-row" if is_playing else ""
        row_num = i + 1
        
        st.markdown(f'<div class="sheet-row {row_class}">', unsafe_allow_html=True)
        st.markdown(f'<div class="row-num">{row_num}</div>', unsafe_allow_html=True)
        
        # Create columns for cells
        c1, c2, c3, c4 = st.columns([80, 400, 250, 120], gap="small")
        
        # CELL A: ID
        with c1:
            st.markdown(f"<div class='cell cell-a' style='border:none;'>{row_num:03d}</div>", unsafe_allow_html=True)
        
        # CELL B: Title (clickable)
        with c2:
            if st.button(f"{track.get('title', 'UNKNOWN')}", key=f"btn_{i}"):
                st.session_state.current_track = track
                st.rerun()
        
        # CELL C: Artist
        with c3:
            st.markdown(f"<div class='cell cell-c' style='border:none;'>{track.get('artist', 'UNKNOWN')}</div>", unsafe_allow_html=True)

        # CELL D: Status
        with c4:
            status = ">" if is_playing else ""
            st.markdown(f"<div class='cell cell-d' style='border:none;'>{status}</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- BOTTOM STATUS BAR ---
    st.markdown(f"""
    <div class="bottom-bar">
        /B-BLANK /C-CLEAR /D-DELETE /E-EDIT /F-FORMAT /G-GLOBAL /I-INSERT /M-MOVE /P-PLAY /Q-QUIT /R-REPLICATE /S-STORAGE /T-TITLES /V-VALUE /W-WINDOW
    </div>
    """, unsafe_allow_html=True)
