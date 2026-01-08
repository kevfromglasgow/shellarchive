import streamlit as st
import streamlit.components.v1 as components
import base64
import json
import requests
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(
    page_title="iPhone 17 // System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. CSS: THE "MESH" AESTHETIC ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

    .stApp {
        background-color: #000000;
        color: #e0e0e0;
        font-family: 'Space Mono', monospace;
    }
    
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem;}

    .wireframe-box {
        border: 1px solid rgba(255, 255, 255, 0.8);
        background: rgba(10, 10, 10, 0.8);
        padding: 25px;
        position: relative;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #000; }
    ::-webkit-scrollbar-thumb { background: #333; border: 1px solid #fff; }

    .enter-btn button {
        border: 1px solid #00FF00 !important;
        color: #00FF00 !important;
        margin-top: 20px;
    }
    .enter-btn button:hover {
        background-color: #00FF00 !important;
        color: black !important;
    }

    .stButton > button {
        width: 100%;
        border: 1px solid #ffffff;
        background-color: transparent;
        color: #ffffff;
        font-family: 'Space Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 15px 0;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #ffffff;
        color: #000000;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
    }
    
    @keyframes bounce {
        0%, 100% { transform: scaleY(1); }
        50% { transform: scaleY(0.4); }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 3D VIEWER COMPONENT ---
def render_interactive_phone(file_path):
    try:
        with open(file_path, "rb") as f:
            b64_model = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"Error: Could not find '{file_path}'")
        return

    pos = "0.000029793852146581127m 0.01536270079792104m 0.004359653040944322m"
    norm = "2.7602458702456583e-7m 7.175783489991045e-8m 0.9999999999999594m"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
        <style>
            body {{ margin: 0; background-color: black; overflow: hidden; }}
            model-viewer {{ width: 100vw; height: 75vh; }}
            
            .hotspot {{
                display: block;
                width: 40px; 
                height: 40px;
                border-radius: 50%;
                cursor: pointer;
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.5); 
                animation: pulse 2s infinite;
                text-decoration: none;
            }}
            .hotspot:hover {{ border-color: #00FF00; background: rgba(0, 255, 0, 0.2); }}

            @keyframes pulse {{
                0% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4); }}
                70% {{ transform: scale(1.1); box-shadow: 0 0 0 15px rgba(255, 255, 255, 0); }}
                100% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }}
            }}
        </style>
    </head>
    <body>
        <model-viewer 
            src="data:model/gltf-binary;base64,{b64_model}"
            camera-controls auto-rotate shadow-intensity="2" exposure="0.6"
            camera-orbit="0deg 90deg 105%" interaction-prompt="none">
            <a class="hotspot" slot="hotspot-trigger" 
               data-position="{pos}" data-normal="{norm}"
               href="?launched=true" target="_top">
            </a>
        </model-viewer>
    </body>
    </html>
    """
    components.html(html_code, height=650)

# --- 3. DATA & AUDIO LOADER (SECURE PROXY) ---

@st.cache_data
def load_secure_playlist():
    """Loads metadata from secrets"""
    try:
        if "PLAYLIST_DATA" in st.secrets:
            return json.loads(st.secrets["PLAYLIST_DATA"])
        else:
            return [{"title": "NO DATA", "artist": "CHECK SECRETS.TOML", "url": ""}]
    except Exception as e:
        st.error(f"Data Error: {e}")
        return []

@st.cache_data(show_spinner=False)
def fetch_audio_bytes(url):
    """
    Downloads the audio from Google Drive to the server ONCE.
    Returns the bytes so Streamlit can serve them directly.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Check for errors (404, etc)
        return response.content
    except Exception as e:
        return None

# --- 4. APP LOGIC ---
query_params = st.query_params
url_launched = query_params.get("launched") == "true"
if 'manual_launch' not in st.session_state:
    st.session_state.manual_launch = False

is_active = url_launched or st.session_state.manual_launch
playlist = load_secure_playlist()

# === VIEW 1: LANDING PAGE ===
if not is_active:
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 2.5em; font-weight: bold; border-bottom: 2px solid white; margin-bottom: 10px;'>IPHONE 17 PRO</div>", unsafe_allow_html=True)
        st.caption("<center>INTERACTIVE MODEL // CLICK THE PULSING LOGO TO UNLOCK</center>", unsafe_allow_html=True)
        
        render_interactive_phone("iPhone 17 Pro.glb")
        
        st.markdown('<div class="enter-btn">', unsafe_allow_html=True)
        if st.button("INITIALIZE SYSTEM [MANUAL ENTER]"):
            st.session_state.manual_launch = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# === VIEW 2: MUSIC APP ===
else:
    if 'track_index' not in st.session_state:
        st.session_state.track_index = 0
    
    if st.session_state.track_index >= len(playlist):
        st.session_state.track_index = 0
        
    current = playlist[st.session_state.track_index]

    # Header
    top_c1, top_c2 = st.columns([1, 6])
    with top_c1:
        if st.button("← EXIT"):
            st.session_state.manual_launch = False
            st.query_params.clear() 
            st.rerun()
    with top_c2:
        st.markdown(f"### // SYSTEM_AUDIO_INTERFACE [{len(playlist)} TRACKS]")

    st.divider()

    # Main Grid
    col_left, col_right = st.columns([1, 1], gap="large")

    # Player UI
    with col_left:
        st.markdown('<div class="wireframe-box">', unsafe_allow_html=True)
        st.caption("STATUS: PLAYING_")
        st.markdown(f"## {current.get('title', 'Unknown')}")
        st.markdown(f"**ARTIST:** {current.get('artist', 'Unknown')}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- PROXY AUDIO PLAYER ---
        if current.get('url'):
            # 1. Fetch bytes from Google (Cached)
            audio_data = fetch_audio_bytes(current['url'])
            
            if audio_data:
                # 2. Serve bytes directly (No URL exposed)
                st.audio(BytesIO(audio_data), format="audio/mp3", autoplay=True)
            else:
                st.error("CONNECTION_ERROR: UNABLE TO STREAM ASSET")
        else:
            st.warning("AUDIO_SOURCE_OFFLINE")
        # --------------------------

        # Visualizer
        st.markdown("""
        <div style="display: flex; gap: 6px; height: 60px; align-items: flex-end; margin-bottom: 25px; margin-top: 10px;">
            <div style="width: 8px; background: white; height: 40%; animation: bounce 1s infinite;"></div>
            <div style="width: 8px; background: white; height: 80%; animation: bounce 1.2s infinite;"></div>
            <div style="width: 8px; background: white; height: 100%; animation: bounce 0.8s infinite;"></div>
            <div style="width: 8px; background: white; height: 60%; animation: bounce 1.5s infinite;"></div>
        </div>
        """, unsafe_allow_html=True)

        # Controls
        b1, b2, b3 = st.columns(3)
        if b1.button("<< PREV"):
            st.session_state.track_index = (st.session_state.track_index - 1) % len(playlist)
            st.rerun()
        if b2.button("|| PAUSE"):
            st.toast("PLAYBACK PAUSED")
        if b3.button("NEXT >>"):
            st.session_state.track_index = (st.session_state.track_index + 1) % len(playlist)
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

    # Queue UI
    with col_right:
        st.markdown('<div class="wireframe-box" style="height: 500px; overflow-y: scroll;">', unsafe_allow_html=True)
        st.markdown("**QUEUE // DATA_STREAM**")
        st.markdown("---")
        
        for i, track in enumerate(playlist):
            active = i == st.session_state.track_index
            
            if active:
                style = "border:1px solid #fff; background:rgba(255,255,255,0.1);"
                prefix = "▶ "
            else:
                style = "border-bottom:1px solid #333; opacity:0.7;"
                prefix = f"{i+1:03}. "

            st.markdown(
                f"<div style='{style}padding:10px;display:flex;justify-content:space-between;'>"
                f"<span>{prefix}{track.get('title', 'Unknown')}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)
