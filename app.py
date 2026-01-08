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
    
    /* REMOVE PADDING to maximize grid space */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 5rem; 
        max-width: 95% !important; /* Force wider layout */
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
    
    /* The main container for the grid */
    .sheet-container {
        border: 3px double #00FF00;
        background: rgba(0, 10, 0, 0.3);
    }

    /* Header Row - strictly defined widths using flex */
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

    /* Data Rows - match flex behavior */
    .sheet-row {
        border-bottom: 1px solid #00FF00;
        min-height: 45px;
        display: flex; /* Ensure row behaves as a flex container */
        align-items: stretch; /* Stretch children to fill height */
    }
    .sheet-row:hover {
        background: rgba(0, 255, 0, 0.08);
    }

    /* Column Definitions - These align with Streamlit column ratios */
    /* Total ratio roughly: 0.5 + 4 + 2 + 1.5 = 8 parts */
    
    .cell {
        padding: 0 10px;
        display: flex;
        align-items: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis; /* Prevents text cutoff */
    }
    
    /* Column A: ID (Small) */
    .col-a { 
        border-right: 1px solid #00FF00; 
        color: #00AA00;
        justify-content: center;
        height: 100%; /* Fill vertical space */
    }
    
    /* Column B: Title (Wide) */
    .col-b { 
        border-right: 1px solid #00FF00; 
        height: 100%;
        width: 100%; /* Fill the streamlit column */
    }
    
    /* Column C: Artist (Medium) */
    .col-c { 
        border-right: 1px solid #00FF00; 
        color: #00DD00;
        height: 100%;
    }
    
    /* Column D: Status (Small/Fixed) */
    .col-d { 
        justify-content: center;
        font-weight: bold;
        height: 100%;
    }

    /* Button Styling - The Critical Fix */
    .stButton {
        width: 100%;
        height: 100%;
        margin: 0;
    }
    .stButton > button {
        border: none;
        background: transparent;
        color: #00FF00;
        text-align: left;
        padding: 8px 0; /* Add vertical padding for clickability */
        margin: 0;
        font-family: 'Share Tech Mono', monospace;
        text-transform: uppercase;
        width: 100%;
        height: 100%;
        line-height: 1.2;
        /* Handle long text in button */
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis; 
    }
    .stButton > button:hover {
        color: #FFFFFF;
        background: transparent;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
    }
    
    /* Active Row Highlight */
    .active-row {
        background: rgba(0, 255, 0, 0.15) !important;
        border-left: 4px solid #00FF00;
    }
    
    /* Player Container */
    .player-container {
        border: 2px solid #00FF00;
        padding: 10px;
        background: rgba(0, 30, 0, 0.5);
        margin-bottom: 20px;
    }
    
    /* Status Indicators */
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
        <div>SYSTEM: WORKBOOK_INTERFACE v2.1.9</div>
        <div>SESSION: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        <div>STATUS: <span style="color:#00FF00;">CONNECTED</span> <span class="blink">█</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Top Navigation & Player ---
    col1, col2 = st.columns([1, 4])
    
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

    # --- SPREADSHEET CONTAINER START ---
    st.markdown('<div class="sheet-container">', unsafe_allow_html=True)

    # --- HEADER ROW (HTML) ---
    # NOTE: We use CSS Grid ratios here to match the columns below
    # Ratios: 1fr (ID) | 6fr (Title) | 3fr (Artist) | 2fr (Status)
    st.markdown("""
        <div class="sheet-header" style="display: flex;">
            <div class="cell col-a" style="flex: 1;">#ID</div>
            <div class="cell col-b" style="flex: 6;">TRACK_TITLE</div>
            <div class="cell col-c" style="flex: 3;">ARTIST_REF</div>
            <div class="cell col-d" style="flex: 2;">STATUS</div>
        </div>
    """, unsafe_allow_html=True)

    # --- DATA ROWS (Loop) ---
    for i, track in enumerate(playlist):
        is_playing = (st.session_state.current_track == track)
        row_class = "active-row" if is_playing else ""
        status_text = "▶ PLAY" if is_playing else "READY"
        status_class = "status-playing" if is_playing else "status-ready"
        
        # Start Row Container
        st.markdown(f'<div class="sheet-row {row_class}">', unsafe_allow_html=True)
        
        # Define Columns with EXACT same ratios as header: 1, 6, 3, 2
        # We use a slight adjustment for Streamlit's internal padding
        c1, c2, c3, c4 = st.columns([1, 6, 3, 2])
        
        # COL 1: ID
        with c1:
            st.markdown(f'<div class="cell col-a" style="height:100%; border:none;">{i+1:03d}</div>', unsafe_allow_html=True)
        
        # COL 2: BUTTON (Title)
        with c2:
            # The key must be unique for every button
            if st.button(f"⟩ {track.get('title', 'Unknown')}", key=f"btn_{i}"):
                st.session_state.current_track = track
                st.rerun()
        
        # COL 3: ARTIST
        with c3:
            st.markdown(f'<div class="cell col-c" style="height:100%; border:none;">{track.get('artist', 'Unknown')}</div>', unsafe_allow_html=True)

        # COL 4: STATUS
        with c4:
            st.markdown(f'<div class="cell col-d {status_class}" style="height:100%; border:none;">{status_text}</div>', unsafe_allow_html=True)
            
        # End Row Container
        st.markdown('</div>', unsafe_allow_html=True)

    # --- SPREADSHEET CONTAINER END ---
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Footer ---
    st.markdown(f"""
    <div class="terminal-header" style="margin-top:20px; font-size:0.8em; text-align:right;">
        END_OF_WORKBOOK // TOTAL_ENTRIES: {len(playlist)}
    </div>
    """, unsafe_allow_html=True)
