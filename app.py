import streamlit as st
import json
import requests
from io import BytesIO

# --- CONFIGURATION ---
# UPDATE THIS to your actual URL (required for the Landing Page button to work)
DEPLOY_URL = "https://shellarchive.streamlit.app"

st.set_page_config(
    page_title="SYSTEM_DATA // XLS",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. RETRO TERMINAL / SPREADSHEET CSS ---
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
    .block-container { padding-top: 2rem; }
    header, footer { visibility: hidden; }

    /* --- LANDING PAGE ICON --- */
    .file-icon-container {
        position: absolute;
        top: 50vh;
        left: 50vw;
        transform: translate(-50%, -50%);
        text-align: center;
    }
    .file-icon {
        font-size: 80px;
        color: #00FF00;
        text-decoration: none;
        border: 2px dashed #00FF00;
        padding: 40px;
        display: block;
        transition: 0.3s;
        background: rgba(0, 255, 0, 0.05);
    }
    .file-icon:hover {
        background: #00FF00;
        color: #000000;
        box-shadow: 0 0 50px rgba(0, 255, 0, 0.5);
    }
    .file-label {
        margin-top: 15px;
        display: block;
        letter-spacing: 2px;
        font-size: 1.2em;
    }

    /* --- SPREADSHEET GRID --- */
    /* The "Grid" Container */
    .sheet-container {
        border: 2px solid #00FF00;
        margin-top: 20px;
    }

    /* Header Row */
    .sheet-header {
        display: flex;
        border-bottom: 2px double #00FF00;
        background: rgba(0, 255, 0, 0.1);
        padding: 10px 0;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Data Rows */
    .sheet-row {
        display: flex;
        border-bottom: 1px dashed #00FF00; /* THE DASHED GREEN LINES */
        align-items: center;
        transition: background 0.2s;
    }
    .sheet-row:hover {
        background: rgba(0, 255, 0, 0.05);
    }

    /* Columns (A, B, C...) */
    .col-a { width: 10%; border-right: 1px dashed #00FF00; padding: 10px; text-align: center; }
    .col-b { width: 45%; border-right: 1px dashed #00FF00; padding: 10px; }
    .col-c { width: 30%; border-right: 1px dashed #00FF00; padding: 10px; }
    .col-d { width: 15%; padding: 10px; text-align: center; }

    /* Button Styling (Making text clickable) */
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
    }
    .stButton > button:hover {
        text-decoration: underline;
        color: #FFFFFF;
        background: transparent;
    }
    /* Active Row Highlight */
    .active-row {
        background: rgba(0, 255, 0, 0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA & PROXY LOGIC ---

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

# --- 3. STATE MANAGEMENT ---
query_params = st.query_params
url_launched = query_params.get("launched") == "true"
if 'manual_launch' not in st.session_state:
    st.session_state.manual_launch = False

# "Active" means we are in the spreadsheet view
is_active = url_launched or st.session_state.manual_launch

if 'current_track' not in st.session_state:
    st.session_state.current_track = None


# ==========================================
# VIEW 1: THE LANDING PAGE (FILE ICON)
# ==========================================
if not is_active:
    # We use raw HTML to create the clickable icon link
    # This bypasses all Streamlit iframe issues.
    st.markdown(f"""
        <div class="file-icon-container">
            <a href="{DEPLOY_URL}/?launched=true" target="_top" class="file-icon">
                [XLS]
                <span class="file-label">ACCESS_WORKBOOK</span>
            </a>
        </div>
    """, unsafe_allow_html=True)


# ==========================================
# VIEW 2: THE INTERACTIVE SPREADSHEET
# ==========================================
else:
    # --- Top Bar (Player & Navigation) ---
    top_col1, top_col2 = st.columns([1, 4])
    
    with top_col1:
        if st.button("<< CLOSE_FILE"):
            st.session_state.manual_launch = False
            st.query_params.clear()
            st.rerun()

    with top_col2:
        # THE AUDIO PLAYER (Sticky Header)
        if st.session_state.current_track:
            track = st.session_state.current_track
            st.write(f"**NOW_PROCESSING:** {track['title']} // {track['artist']}")
            
            # Proxy Fetch
            if track.get('url'):
                audio_data = fetch_audio_bytes(track['url'])
                if audio_data:
                    st.audio(BytesIO(audio_data), format="audio/mp3", autoplay=True)
                else:
                    st.error("ERR_CONNECTION_REFUSED")

    st.write("---")

    # --- THE SPREADSHEET HEADER ---
    st.markdown("""
    <div class="sheet-container">
        <div class="sheet-header">
            <div class="col-a">ID</div>
            <div class="col-b">TRACK_TITLE (CLICK_TO_LOAD)</div>
            <div class="col-c">ARTIST_REF</div>
            <div class="col-d">STATUS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- THE SPREADSHEET ROWS (Generated via Loop) ---
    # We use st.columns inside the loop to create the grid structure.
    # CSS classes handles the "Dashed Green Lines".
    
    for i, track in enumerate(playlist):
        
        # Determine if this row is playing
        is_playing = (st.session_state.current_track == track)
        row_style = "active-row" if is_playing else ""
        status_icon = "[[ PLAYING ]]" if is_playing else "READY"
        
        # Grid Layout
        c1, c2, c3, c4 = st.columns([1, 4.5, 3, 1.5])
        
        # COLUMN A: ID
        with c1:
            st.markdown(f"<div class='col-a {row_style}' style='border:none; width:100%; text-align:center;'>{i+1:03}</div>", unsafe_allow_html=True)
        
        # COLUMN B: CLICKABLE TITLE (The Interaction)
        with c2:
            # We use a Streamlit button that looks like plain text via CSS
            if st.button(f"{track.get('title', 'Unknown')}", key=f"btn_{i}"):
                st.session_state.current_track = track
                st.rerun()
        
        # COLUMN C: ARTIST
        with c3:
             st.markdown(f"<div class='col-c {row_style}' style='border:none; width:100%;'>{track.get('artist', 'Unknown')}</div>", unsafe_allow_html=True)

        # COLUMN D: STATUS
        with c4:
             st.markdown(f"<div class='col-d {row_style}' style='border:none; width:100%; text-align:center;'>{status_icon}</div>", unsafe_allow_html=True)
             
        # Divider (The Dashed Line between rows)
        st.markdown(f"<div style='border-bottom: 1px dashed #004400; margin-bottom: 5px;'></div>", unsafe_allow_html=True)
