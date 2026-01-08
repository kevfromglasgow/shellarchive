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
    
    /* HIDE DEFAULT ELEMENTS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem;}

    /* WIREFRAME CONTAINER STYLE */
    .wireframe-box {
        border: 1px solid rgba(255, 255, 255, 0.8);
        background: rgba(10, 10, 10, 0.8);
        padding: 25px;
        position: relative;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.05);
    }

    /* GHOST BUTTONS */
    .stButton > button {
        width: 100%;
        border: 1px solid #ffffff;
        background-color: transparent;
        color: #ffffff;
        border-radius: 0px;
        font-family: 'Space Mono', monospace;
        text-transform: uppercase;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #ffffff;
        color: #000000;
        border-color: #ffffff;
        box-shadow: 0 0 8px #ffffff;
    }
    
    /* TEXT UTILS */
    .h-glitch {
        font-size: 2em;
        font-weight: bold;
        letter-spacing: -1px;
        border-bottom: 2px solid white;
        margin-bottom: 20px;
        display: inline-block;
    }
    .small-meta {
        font-size: 0.7em;
        opacity: 0.6;
        margin-bottom: 10px;
        display: block;
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

    # User provided coordinates
    pos = "0.000029793852146581127m 0.01536270079792104m 0.004359653040944322m"
    norm = "2.7602458702456583e-7m 7.175783489991045e-8m 0.9999999999999594m"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
        <style>
            body {{ margin: 0; background-color: black; overflow: hidden; }}
            model-viewer {{ width: 100vw; height: 80vh; }}
            
            /* THE INVISIBLE TRIGGER OVER THE LOGO */
            .hotspot {{
                display: block;
                width: 30px; 
                height: 30px;
                border-radius: 50%;
                cursor: pointer;
                background: transparent;
                border: 1px dashed rgba(255, 255, 255, 0.5); /* Semi-visible for feedback */
                animation: pulse 2s infinite;
            }}
            
            .hotspot:hover {{
                border: 1px solid #fff;
                background: rgba(255, 255, 255, 0.2);
            }}

            @keyframes pulse {{
                0% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7); }}
                70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 255, 255, 0); }}
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
                // RELOAD PAGE WITH QUERY PARAM TO TRIGGER PYTHON STATE
                const url = new URL(window.parent.location.href);
                url.searchParams.set('launched', 'true');
                window.parent.location.href = url.toString();
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=700)


# --- 3. APP LOGIC FLOW ---

# Check Query Parameters to see if user "Clicked" the phone
query_params = st.query_params
is_launched = query_params.get("launched") == "true"

# --- VIEW A: THE 3D LANDING PAGE ---
if not is_launched:
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<span class='h-glitch'>IPHONE 17 PRO</span>", unsafe_allow_html=True)
        st.caption("SYSTEM LOCKED // TAP LOGO TO INITIALIZE")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # RENDER THE PHONE
        render_interactive_phone("iPhone 17 Pro.glb")

# --- VIEW B: THE MUSIC APP (MESH UI) ---
else:
    # 1. HEADER
    top_c1, top_c2 = st.columns([1, 6])
    with top_c1:
        # Reset URL to go back
        if st.button("← EXIT"):
            st.query_params.clear() # Clears ?launched=true
            st.rerun()
            
    with top_c2:
        st.markdown("### // AUDIO_INTERFACE_V1")

    st.divider()

    # 2. MAIN CONTENT GRID
    col_left, col_right = st.columns([1, 1], gap="large")

    # LEFT: Now Playing
    with col_left:
        st.markdown('<div class="wireframe-box">', unsafe_allow_html=True)
        st.markdown("<span class='small-meta'>STATUS: PLAYING_</span>", unsafe_allow_html=True)
        st.markdown("## NEON HORIZONS")
        st.markdown("**ARTIST:** SYSTEM_ID_909")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # CSS Visualizer
        st.markdown("""
        <div style="display: flex; align-items: flex-end; justify-content: space-between; height: 60px; margin-bottom: 30px;">
            <div style="width: 8px; background: #fff; height: 40%;"></div>
            <div style="width: 8px; background: #fff; height: 80%;"></div>
            <div style="width: 8px; background: #fff; height: 30%;"></div>
            <div style="width: 8px; background: #fff; height: 100%;"></div>
            <div style="width: 8px; background: #fff; height: 60%;"></div>
            <div style="width: 8px; background: #fff; height: 20%;"></div>
            <div style="width: 8px; background: #fff; height: 90%;"></div>
            <div style="width: 8px; background: #fff; height: 50%;"></div>
        </div>
        """, unsafe_allow_html=True)

        # Controls
        b1, b2, b3 = st.columns(3)
        b1.button("<< PREV")
        b2.button("|| PAUSE")
        b3.button("NEXT >>")
        st.markdown('</div>', unsafe_allow_html=True)

    # RIGHT: Playlist
    with col_right:
        st.markdown('<div class="wireframe-box">', unsafe_allow_html=True)
        st.markdown("<span class='small-meta'>QUEUE_DATA</span>", unsafe_allow_html=True)
        
        playlist_data = [
            {"id": "01", "title": "Mainframe Access", "time": "3:42"},
            {"id": "02", "title": "Binary Soul", "time": "4:20"},
            {"id": "03", "title": "Voltage_Spike", "time": "2:15"},
            {"id": "04", "title": "Zero_Day_Exploit", "time": "3:33"},
        ]
        
        for track in playlist_data:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #333;">
                <span>{track['id']} // {track['title']}</span>
                <span style="opacity: 0.5;">{track['time']}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)