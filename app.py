import streamlit as st
import streamlit.components.v1 as components
import base64
import requests
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(
    page_title="iPhone 17 // System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- GLOBAL STYLES ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');

.stApp {
    background-color: #000;
    color: #e0e0e0;
    font-family: 'Space Mono', monospace;
}

header, footer {visibility: hidden;}
.block-container {padding-top: 1rem;}

.wireframe-box {
    border: 1px solid rgba(255,255,255,0.8);
    background: rgba(10,10,10,0.8);
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 0 20px rgba(255,255,255,0.05);
}

.enter-button button {
    border: 1px solid #00FF00 !important;
    color: #00FF00 !important;
    box-shadow: 0 0 10px rgba(0,255,0,0.2);
}

.enter-button button:hover {
    background-color: #00FF00 !important;
    color: black !important;
    box-shadow: 0 0 20px rgba(0,255,0,0.6);
}

.stButton > button {
    width: 100%;
    border: 1px solid #fff;
    background-color: transparent;
    color: #fff;
    letter-spacing: 2px;
    padding: 15px 0;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background-color: #fff;
    color: #000;
    box-shadow: 0 0 15px rgba(255,255,255,0.5);
}

@keyframes bounce {
    0%, 100% { transform: scaleY(1); }
    50% { transform: scaleY(0.4); }
}
</style>
""", unsafe_allow_html=True)

# --- STREAMLIT MESSAGE LISTENER ---
components.html("""
<script>
window.addEventListener("message", (event) => {
    if (event.data === "LAUNCH_SYSTEM") {
        const url = new URL(window.top.location.href);
        url.searchParams.set("launched", "true");
        window.top.location.href = url.toString();
    }
});
</script>
""", height=0)

# --- AUDIO PROXY ---
def stream_audio(track_url):
    response = requests.get(track_url, stream=True)
    audio_bytes = BytesIO(response.content)
    st.audio(audio_bytes, format="audio/mp3")

# --- 3D VIEWER WITH SCAN + BIOMETRIC ---
def render_interactive_phone(file_path):
    with open(file_path, "rb") as f:
        b64_model = base64.b64encode(f.read()).decode()

    pos = "0.000029793852146581127m 0.01536270079792104m 0.004359653040944322m"
    norm = "2.7602458702456583e-7m 7.175783489991045e-8m 0.9999999999999594m"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
<style>
body {{ margin: 0; background: black; overflow: hidden; }}

model-viewer {{ width: 100vw; height: 70vh; }}

.hotspot {{
    width: 35px;
    height: 35px;
    border-radius: 50%;
    cursor: pointer;
    background: rgba(255,255,255,0.05);
    border: 1px dashed rgba(255,255,255,0.6);
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0% {{ transform: scale(0.9); }}
    50% {{ transform: scale(1.1); }}
    100% {{ transform: scale(0.9); }}
}}

#scan-line {{
    position: absolute;
    top: 0;
    width: 100%;
    height: 4px;
    background: #00ffcc;
    box-shadow: 0 0 20px #00ffcc;
    animation: scan 2.5s linear forwards;
    display: none;
}}

@keyframes scan {{
    from {{ top: 0; }}
    to {{ top: 100%; }}
}}

#biometric {{
    position: absolute;
    bottom: 40px;
    left: 50%;
    transform: translateX(-50%);
    width: 300px;
    border: 1px solid #00ffcc;
    padding: 6px;
    display: none;
}}

#bar {{
    width: 0%;
    height: 12px;
    background: #00ffcc;
    transition: width 0.1s linear;
}}

#status {{
    text-align: center;
    font-size: 12px;
    margin-top: 6px;
    color: #00ffcc;
}}
</style>
</head>

<body>
<div id="scan-line"></div>

<div id="biometric">
    <div id="bar"></div>
    <div id="status">SCANNING BIOMETRICS...</div>
</div>

<model-viewer 
    src="data:model/gltf-binary;base64,{b64_model}"
    camera-controls
    auto-rotate
    exposure="0.6"
    camera-orbit="0deg 90deg 105%"
    interaction-prompt="none">

    <button class="hotspot"
        slot="hotspot-trigger"
        data-position="{pos}"
        data-normal="{norm}"
        onclick="startScan()">
    </button>
</model-viewer>

<script>
function startScan() {{
    const scan = document.getElementById("scan-line");
    const bio = document.getElementById("biometric");
    const bar = document.getElementById("bar");
    const status = document.getElementById("status");

    scan.style.display = "block";
    bio.style.display = "block";

    let progress = 0;
    const interval = setInterval(() => {{
        progress += 2;
        bar.style.width = progress + "%";

        if (progress >= 100) {{
            clearInterval(interval);
            status.innerText = "IDENTITY VERIFIED";
            setTimeout(() => {{
                window.parent.postMessage("LAUNCH_SYSTEM", "*");
            }}, 600);
        }}
    }}, 50);
}}
</script>
</body>
</html>
"""
    components.html(html, height=600)

# --- APP STATE ---
query_params = st.query_params
url_launched = query_params.get("launched") == "true"

if "manual_launch" not in st.session_state:
    st.session_state.manual_launch = False

is_active = url_launched or st.session_state.manual_launch

# --- TRACK MAP ---
track_map = {
    0: st.secrets["TRACK1"],
    1: st.secrets["TRACK2"],
    2: st.secrets["TRACK3"],
}

playlist = [
    {"title": "NEON HORIZONS", "artist": "SYSTEM_ID_909", "length": "3:42"},
    {"title": "MAINFRAME ACCESS", "artist": "BINARY_SOUL", "length": "2:15"},
    {"title": "VOLTAGE SPIKE", "artist": "NULL_POINTER", "length": "4:01"},
]

# === LANDING PAGE ===
if not is_active:
    col1, col2, col3 = st.columns([1,8,1])
    with col2:
        st.markdown("<div style='text-align:center;font-size:2.5em;font-weight:bold;border-bottom:2px solid white;'>IPHONE 17 PRO</div>", unsafe_allow_html=True)
        st.caption("<center>INTERACTIVE MODEL // TAP LOGO TO SCAN</center>", unsafe_allow_html=True)

        render_interactive_phone("iPhone 17 Pro.glb")

        st.markdown('<div class="enter-button">', unsafe_allow_html=True)
        if st.button("INITIALIZE SYSTEM [ENTER]"):
            st.session_state.manual_launch = True
            st.query_params["launched"] = "true"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# === MUSIC SYSTEM ===
else:
    if "track_index" not in st.session_state:
        st.session_state.track_index = 0

    current = playlist[st.session_state.track_index]
    current_url = track_map[st.session_state.track_index]

    c1, c2 = st.columns([1,6])
    with c1:
        if st.button("← EXIT"):
            st.session_state.manual_launch = False
            st.query_params.clear()
            st.rerun()
    with c2:
        st.markdown("### // SYSTEM_AUDIO_INTERFACE")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="wireframe-box">', unsafe_allow_html=True)
        st.caption("STATUS: PLAYING_")
        st.markdown(f"## {current['title']}")
        st.markdown(f"**ARTIST:** {current['artist']}")

        stream_audio(current_url)

        st.markdown("""
        <div style="display:flex;gap:6px;height:60px;align-items:flex-end;">
            <div style="width:8px;background:white;height:40%;animation:bounce 1s infinite;"></div>
            <div style="width:8px;background:white;height:80%;animation:bounce 1.2s infinite;"></div>
            <div style="width:8px;background:white;height:100%;animation:bounce 0.8s infinite;"></div>
        </div>
        """, unsafe_allow_html=True)

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

    with right:
        st.markdown('<div class="wireframe-box">', unsafe_allow_html=True)
        st.markdown("**QUEUE // DATA_STREAM**")
        st.markdown("---")

        for i, track in enumerate(playlist):
            active = i == st.session_state.track_index
            style = "border:1px solid #fff;background:rgba(255,255,255,0.1);" if active else "border-bottom:1px solid #333;opacity:0.7;"
            prefix = "▶ " if active else f"0{i+1}. "
            st.markdown(
                f"<div style='{style}padding:10px;display:flex;justify-content:space-between;'>"
                f"<span>{prefix}{track['title']}</span>"
                f"<span>{track['length']}</span></div>",
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)
