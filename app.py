import streamlit as st
import streamlit.components.v1 as components
import base64

# --- CONFIGURATION ---
st.set_page_config(
    page_title="iPhone 17 // System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. CSS: THE "MESH/WIREFRAME" AESTHETIC ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

    /* GLOBAL DARK MODE */
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
        font-family: 'Space Mono', monospace;
    }
    
    /* HIDE DEFAULT STREAMLIT ELEMENTS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem;}

    /* WIREFRAME BOXES (The "Mesh" Look) */
    .wireframe-box {
        border: 1px solid rgba(255, 255, 255, 0.8);
        background: rgba(10, 10, 10, 0.8);
        padding: 25px;
        position: relative;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
    }

    /* CUSTOM BUTTONS */
    .stButton > button {
        width: 100%;
        border: 1px solid #ffffff;
        background-color: transparent;
        color: #ffffff;
        border-radius: 0px;
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
        border-color: #ffffff;
    }
    
    /* ANIMATIONS */
    @keyframes bounce {
        0%, 100% { transform: scaleY(1); }
        50% { transform: scaleY(0.4); }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 3D VIEWER COMPONENT ---
def render_interactive_phone(file_path):
    """
    Renders the GLB. When the specific hotspot is clicked, 
    JavaScript reloads the page with '?launched=true'.
    """
    try:
        with open(file_path, "rb") as f:
            b64_model = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"Error: Could not find '{file_path}' in the directory.")
        return

    # Specific coordinates for the Apple Logo on iPhone 17 Pro
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
            
            /* THE INVISIBLE TRIGGER OVER THE LOGO */
            .hotspot {{
                display: block;
                width: 35px; 
                height: 35px;
                border-radius: 50%;
                cursor: pointer;
                background: rgba(255, 255, 255, 0.05);
                border: 1px dashed rgba(255, 255, 255, 0.3); 
                animation: pulse 2s infinite;
            }}
            
            .hotspot:hover {{
                border: 1px solid #fff;
                background: rgba(255, 255, 255, 0.3);
            }}

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
            camera-controls
            auto-rotate
            shadow-intensity="2"
            exposure="0.6"
            camera-orbit="0deg 90deg 105%"
            interaction-prompt="none"
        >
            <button class="hotspot" 
                    slot="hotspot-trigger" 
                    data-position="{pos}" 
                    data-normal="{norm}"
                    onclick="triggerLaunch()">
            </button>
        </model-viewer>

        <script>
            function triggerLaunch() {{
                // Visual feedback
                alert("ACCESS GRANTED... LOADING SYSTEM.");
                
                // Navigate to launched state
                try {{
                    const url = new URL(window.top.location.href);
                    url.searchParams.set('launched', 'true');
                    window.top.location.href = url.toString();
                }} catch(e) {{
                    // Fallback for strict iframes
                    console.error(e);
                }}
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=650)


# --- 3. APP LOGIC FLOW ---

# Check Query Parameters & Session State
query_params = st.query_params
url_launched = query_params.get("launched") == "true"

if 'manual_launch' not in st.session_state:
    st.session_state.manual_launch = False

# Determine if we are in the "Active" state
is_active = url_launched or st.session_state.manual_launch

# --- VIEW A: THE 3D LANDING PAGE ---
if not is_active:
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; font-size: 2.5em; font-weight: bold; border-bottom: 2px solid white; margin-bottom: 10px;'>IPHONE 17 PRO</div>", unsafe_allow_html=True)
        st.caption("<center>INTERACTIVE MODEL // CLICK THE PULSING LOGO TO UNLOCK</center>", unsafe_allow_html=True)
        
        # RENDER THE PHONE
        # Ensure 'iPhone 17 Pro.glb' is in the root directory
        render_interactive_phone("iPhone 17 Pro.glb")
        
        # Fallback Button (Crucial for Mobile/Strict Browsers)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ENTER SYSTEM [MANUAL OVERRIDE]"):
            st.session_state.manual_launch = True
            st.rerun()

# --- VIEW B: THE MUSIC APP (FUNCTIONAL) ---
else:
    # 1. SETUP PLAYLIST & STATE
    # Note: For audio to play, place actual .mp3 files in your folder and update filenames below.
    # If files are missing, the UI will still work, but no sound will play.
    playlist = [
        {"title": "NEON HORIZONS", "artist": "SYSTEM_ID_909", "file": "song1.mp3", "length": "3:42"},
        {"title": "MAINFRAME ACCESS", "artist": "BINARY_SOUL", "file": "song2.mp3", "length": "2:15"},
        {"title": "VOLTAGE SPIKE", "artist": "NULL_POINTER", "file": "song3.mp3", "length": "4:01"},
        {"title": "ZERO DAY", "artist": "KERNEL_PANIC", "file": "song4.mp3", "length": "3:10"},
    ]

    if 'track_index' not in st.session_state:
        st.session_state.track_index = 0
    
    current_track = playlist[st.session_state.track_index]

    # 2. HEADER
    top_c1, top_c2 = st.columns([1, 6])
    with top_c1:
        if st.button("← EXIT"):
            st.session_state.manual_launch = False
            st.query_params.clear() # Clears ?launched=true
            st.rerun()
            
    with top_c2:
        st.markdown("### // AUDIO_INTERFACE_V1")

    st.divider()

    # 3. MAIN CONTENT GRID
    col_left, col_right = st.columns([1, 1], gap="large")

    # LEFT: Now Playing & Controls
    with col_left:
        st.markdown('<div class="wireframe-box">', unsafe_allow_html=True)
        st.caption("STATUS: PLAYING_")
        st.markdown(f"## {current_track['title']}")
        st.markdown(f"**ARTIST:** {current_track['artist']}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Try to play audio (will fail gracefully if file missing)
        try:
            st.audio(current_track['file'], format='audio/mp3')
        except:
            pass # Suppress error if files don't exist yet

        # CSS Visualizer
        st.markdown("""
        <div style="display: flex; gap: 6px; height: 60px; align-items: flex-end; margin-bottom: 25px; margin-top: 10px;">
            <div style="width: 8px; background: white; height: 40%; animation: bounce 1s infinite;"></div>
            <div style="width: 8px; background: white; height: 80%; animation: bounce 1.2s infinite;"></div>
            <div style="width: 8px; background: white; height: 100%; animation: bounce 0.8s infinite;"></div>
            <div style="width: 8px; background: white; height: 60%; animation: bounce 1.5s infinite;"></div>
            <div style="width: 8px; background: white; height: 30%; animation: bounce 1.1s infinite;"></div>
            <div style="width: 8px; background: white; height: 70%; animation: bounce 0.9s infinite;"></div>
            <div style="width: 8px; background: white; height: 50%; animation: bounce 1.3s infinite;"></div>
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

    # RIGHT: Playlist Queue
    with col_right:
        st.markdown('<div class="wireframe-box">', unsafe_allow_html=True)
        st.markdown("**QUEUE // DATA_STREAM**")
        st.markdown("---")
        
        for i, track in enumerate(playlist):
            # Styling for active vs inactive tracks
            if i == st.session_state.track_index:
                style = "border: 1px solid #fff; padding: 10px; background: rgba(255,255,255,0.1); font-weight: bold;"
                prefix = "▶ "
            else:
                style = "border-bottom: 1px solid #333; padding: 10px; opacity: 0.7;"
                prefix = f"0{i+1}. "
            
            st.markdown(f"""
            <div style="{style} display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>{prefix}{track['title']}</span>
                <span>{track['length']}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
