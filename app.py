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
    .block-container { 
        padding-top: 0; 
        padding-bottom: 0;
        max-width: 100%;
    }
    header, footer { visibility: hidden; }

    /* --- 3D CANVAS CONTAINER --- */
    #canvas-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 1;
    }
    
    /* Workbook content (hidden, used for texture) */
    #workbook-content {
        position: absolute;
        left: -9999px;
        width: 1400px;
        background: #000000;
        padding: 20px;
    }

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
        background: rgba(0, 20, 0, 0.95);
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
        background: rgba(0, 10, 0, 0.95);
        box-shadow: 
            0 0 20px rgba(0, 255, 0, 0.2),
            inset 0 0 20px rgba(0, 0, 0, 0.5);
    }

    /* Header Row */
    .sheet-header {
        display: flex;
        border-bottom: 3px double #00FF00;
        background: rgba(0, 50, 0, 0.95);
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
        background: rgba(0, 30, 0, 0.95);
        margin-bottom: 10px;
        box-shadow: 
            0 0 15px rgba(0, 255, 0, 0.2),
            inset 0 0 10px rgba(0, 0, 0, 0.5);
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
    
    .glitch {
        animation: glitch-skew 2s infinite;
    }
    
    @keyframes glitch-skew {
        0% { transform: skew(0deg); }
        10% { transform: skew(-2deg); }
        20% { transform: skew(2deg); }
        30% { transform: skew(0deg); }
        100% { transform: skew(0deg); }
    }
    
    /* Controls overlay */
    .controls-overlay {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10000;
        background: rgba(0, 20, 0, 0.9);
        border: 2px solid #00FF00;
        padding: 10px 20px;
        color: #00FF00;
        font-size: 0.9em;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
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
# VIEW 2: 3D WORKBOOK
# ==========================================
else:
    # Hidden content div for rendering
    st.markdown('<div id="workbook-content">', unsafe_allow_html=True)
    
    # Terminal Header
    st.markdown(f"""
    <div class="terminal-header">
        <div>SYSTEM: WORKBOOK_INTERFACE v2.1.9</div>
        <div>SESSION: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        <div>STATUS: <span style="color:#00FF00;">CONNECTED</span> <span class="blink">█</span></div>
        <div>RECORDS_LOADED: {len(playlist):03d}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Top Navigation & Player
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("◄◄ CLOSE_FILE", key="close"):
            st.session_state.manual_launch = False
            st.query_params.clear()
            st.rerun()

    with col2:
        if st.session_state.current_track:
            track = st.session_state.current_track
            st.markdown(f"""
            <div class="player-container">
                <div style="color:#00FF00; font-weight:bold;">
                    ▶ NOW_PROCESSING: {track['title']} // {track['artist']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if track.get('url'):
                audio_data = fetch_audio_bytes(track['url'])
                if audio_data:
                    st.audio(BytesIO(audio_data), format="audio/mp3", autoplay=True)

    # Spreadsheet
    st.markdown("""
    <div class="sheet-container">
        <div class="sheet-header">
            <div class="col-a">#ID</div>
            <div class="col-b">TRACK_TITLE [CLICK_TO_EXECUTE]</div>
            <div class="col-c">ARTIST_REFERENCE</div>
            <div class="col-d">STATUS</div>
        </div>
    """, unsafe_allow_html=True)

    for i, track in enumerate(playlist):
        is_playing = (st.session_state.current_track == track)
        row_class = "active-row" if is_playing else ""
        status_class = "status-playing" if is_playing else "status-ready"
        status_text = "▶ PLAY" if is_playing else "READY"
        
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="terminal-header" style="margin-top:20px; font-size:0.8em;">
        <div>END_OF_WORKBOOK // TOTAL_ENTRIES: {len(playlist)} // MEMORY_USAGE: OK</div>
    </div>
    </div><!-- Close workbook-content -->
    
    <div id="canvas-container"></div>
    
    <div class="controls-overlay">
        DRAG: Rotate | SCROLL: Zoom | RIGHT-CLICK + DRAG: Pan
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    (function() {{
        const container = document.getElementById('canvas-container');
        const workbookContent = document.getElementById('workbook-content');
        
        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000);
        
        // Camera
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 5;
        
        // Renderer
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        container.appendChild(renderer.domElement);
        
        // Grid helper (cyber grid floor)
        const gridHelper = new THREE.GridHelper(20, 20, 0x00ff00, 0x003300);
        gridHelper.rotation.x = Math.PI / 2;
        gridHelper.position.z = -2;
        scene.add(gridHelper);
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0x00ff00, 0.5);
        scene.add(ambientLight);
        
        const pointLight = new THREE.PointLight(0x00ff00, 1, 100);
        pointLight.position.set(0, 0, 10);
        scene.add(pointLight);
        
        // Create workbook plane with HTML texture
        const planeGeometry = new THREE.PlaneGeometry(8, 6);
        const planeMaterial = new THREE.MeshBasicMaterial({{ 
            color: 0x00ff00,
            wireframe: false,
            transparent: true,
            opacity: 0.95
        }});
        const plane = new THREE.Mesh(planeGeometry, planeMaterial);
        scene.add(plane);
        
        // Wireframe border
        const edgesGeometry = new THREE.EdgesGeometry(planeGeometry);
        const edgesMaterial = new THREE.LineBasicMaterial({{ color: 0x00ff00, linewidth: 2 }});
        const wireframe = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        plane.add(wireframe);
        
        // Mouse controls
        let isDragging = false;
        let isPanning = false;
        let previousMousePosition = {{ x: 0, y: 0 }};
        
        renderer.domElement.addEventListener('mousedown', (e) => {{
            if (e.button === 0) {{ // Left click
                isDragging = true;
            }} else if (e.button === 2) {{ // Right click
                isPanning = true;
            }}
            previousMousePosition = {{ x: e.clientX, y: e.clientY }};
        }});
        
        renderer.domElement.addEventListener('mousemove', (e) => {{
            if (isDragging) {{
                const deltaX = e.clientX - previousMousePosition.x;
                const deltaY = e.clientY - previousMousePosition.y;
                
                plane.rotation.y += deltaX * 0.01;
                plane.rotation.x += deltaY * 0.01;
            }} else if (isPanning) {{
                const deltaX = e.clientX - previousMousePosition.x;
                const deltaY = e.clientY - previousMousePosition.y;
                
                plane.position.x += deltaX * 0.01;
                plane.position.y -= deltaY * 0.01;
            }}
            
            previousMousePosition = {{ x: e.clientX, y: e.clientY }};
        }});
        
        renderer.domElement.addEventListener('mouseup', () => {{
            isDragging = false;
            isPanning = false;
        }});
        
        renderer.domElement.addEventListener('contextmenu', (e) => {{
            e.preventDefault();
        }});
        
        // Zoom with mouse wheel
        renderer.domElement.addEventListener('wheel', (e) => {{
            e.preventDefault();
            camera.position.z += e.deltaY * 0.01;
            camera.position.z = Math.max(2, Math.min(20, camera.position.z));
        }});
        
        // Window resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        // Animation loop
        function animate() {{
            requestAnimationFrame(animate);
            
            // Subtle auto-rotation when not interacting
            if (!isDragging && !isPanning) {{
                plane.rotation.y += 0.001;
            }}
            
            // Pulsing glow effect
            wireframe.material.opacity = 0.5 + Math.sin(Date.now() * 0.002) * 0.3;
            
            renderer.render(scene, camera);
        }}
        
        animate();
    }})();
    </script>
    """, unsafe_allow_html=True)
