import streamlit as st
import random
from datetime import datetime
from streamlit_js_eval import get_geolocation

# ================= 1. GPS LOGIC (STABLE) =================
with col_gps:
    st.write("##")
    if st.button("📍 Auto-Detect (GPS)", use_container_width=True):
        location = get_geolocation()
        
        # We use a small toast to let the user know we are working
        with st.spinner("Fetching GPS..."):
            if location and "coords" in location:
                lat = location['coords']['latitude']
                lon = location['coords']['longitude']
                
                detected = get_city_name(lat, lon)
                
                if detected:
                    st.session_state.city_name = detected
                    st.success(f"Found: {detected}")
                    st.rerun()
                else:
                    st.warning("Coordinates found, but city name failed. Resetting to Suryapet.")
                    st.session_state.city_name = "Suryapet"
                    st.rerun()
            else:
                st.error("⚠️ GPS access denied. Please check browser permissions.")

# ================= 2. GLOBAL ANIMATION STYLES =================
# We define keyframes once to keep the DOM clean
st.markdown("""
<style>
    /* Keyframes for Rain */
    @keyframes rain-fall {
        from { transform: translateY(-10vh); }
        to { transform: translateY(110vh); }
    }
    
    /* Keyframes for Clouds */
    @keyframes cloud-move {
        from { left: -250px; }
        to { left: 110vw; }
    }

    /* Keyframes for Sun/Moon Pulse */
    @keyframes celestial-pulse {
        0%, 100% { opacity: 0.4; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.1); }
    }

    /* Critical: Prevent animations from blocking mouse clicks */
    .weather-effect {
        pointer-events: none;
        position: fixed;
        z-index: 0;
    }

    /* Ensure UI content stays on top */
    .block-container { 
        position: relative; 
        z-index: 10; 
    }
</style>
""", unsafe_allow_html=True)

# ================= 3. WEATHER EFFECTS (DYNAMIC) =================
condition = w["weather"][0]["main"].lower()
hour = datetime.now().hour

# --- SUN / MOON ---
if "clear" in condition:
    is_day = 6 <= hour < 18
    color = "#FFD54F" if is_day else "#ffffff"
    size = "150px" if is_day else "100px"
    glow = "70%" if is_day else "50%"
    
    st.markdown(f"""
        <div class="weather-effect" style="
            top: 80px;
            right: 80px;
            width: {size};
            height: {size};
            background: radial-gradient(circle, {color} 0%, transparent {glow});
            filter: blur(15px);
            animation: celestial-pulse 4s ease-in-out infinite;
        "></div>
    """, unsafe_allow_html=True)

# --- RAIN ---
if "rain" in condition or "drizzle" in condition:
    rain_drops = ""
    for _ in range(50):
        left = random.randint(0, 100)
        dur = random.uniform(0.6, 1.3)
        delay = random.uniform(0, 2)
        rain_drops += f'<div class="weather-effect rain" style="left:{left}%; width:2px; height:20px; background:rgba(255,255,255,0.4); animation: rain-fall {dur}s linear {delay}s infinite;"></div>'
    st.markdown(rain_drops, unsafe_allow_html=True)

# --- CLOUDS (ALWAYS ON) ---
cloud_html = ""
for i in range(8):
    top = random.randint(50, 400)
    speed = random.randint(60, 120)
    delay = random.randint(-120, 0)
    opacity = random.uniform(0.2, 0.5)
    scale = random.uniform(0.8, 1.5)
    
    cloud_html += f"""
    <div class="weather-effect" style="
        top: {top}px;
        width: 200px;
        height: 60px;
        background: radial-gradient(circle at 30% 50%, white 40%, transparent 70%),
                    radial-gradient(circle at 60% 40%, white 35%, transparent 70%),
                    radial-gradient(circle at 80% 60%, white 30%, transparent 70%);
        filter: blur(15px);
        opacity: {opacity};
        transform: scale({scale});
        animation: cloud-move {speed}s linear {delay}s infinite;
        border-radius: 50px;
    "></div>
    """
st.markdown(cloud_html, unsafe_allow_html=True)
