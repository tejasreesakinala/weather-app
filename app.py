import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
from difflib import get_close_matches
import random

# ================= CONFIG =================
API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"
st.set_page_config(page_title="Weather Pro", layout="wide")

# ================= GLOBAL STATE =================
if "weather_condition" not in st.session_state:
    st.session_state.weather_condition = None

# ================= UI STYLE =================
st.markdown("""
<style>

/* ===== BACKGROUND ===== */
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1c92d2);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    color: white;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* ===== CARD ===== */
.card {
    background: rgba(255,255,255,0.12);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0 0 30px rgba(0,0,0,0.2);
}

/* ===== CLOUD SYSTEM ===== */
.cloud {
    position: fixed;
    pointer-events: none;
    animation: cloudMove linear infinite;
    z-index: 0;
}

.cloud.back { animation-duration: 160s; opacity: 0.25; }
.cloud.mid { animation-duration: 90s; opacity: 0.5; }
.cloud.front { animation-duration: 45s; opacity: 0.85; }

@keyframes cloudMove {
    from { transform: translateX(-150vw); }
    to { transform: translateX(120vw); }
}

/* ===== SUN ===== */
.sun {
    position: fixed;
    top: 80px;
    right: 120px;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, #FFD700, #FF8C00);
    border-radius: 50%;
    box-shadow: 0 0 80px rgba(255,200,0,0.6);
    animation: sunMove 6s ease-in-out infinite;
}

@keyframes sunMove {
    0% { transform: translateY(0); }
    50% { transform: translateY(-25px); }
    100% { transform: translateY(0); }
}

/* ===== RAIN ===== */
.rain {
    position: fixed;
    width: 2px;
    height: 15px;
    background: rgba(255,255,255,0.5);
    animation: rainFall linear infinite;
}

@keyframes rainFall {
    from { transform: translateY(-100px); }
    to { transform: translateY(100vh); }
}

/* UI ABOVE */
.block-container {
    position: relative;
    z-index: 1;
}

</style>
""", unsafe_allow_html=True)

st.title("🌤 Weather Pro Dashboard")

# Fix HTML rendering bug
st.markdown("<div></div>", unsafe_allow_html=True)

# ================= CLOUD SVG =================
cloud_svg = """
<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="soft">
      <feGaussianBlur stdDeviation="4"/>
    </filter>
  </defs>
  <g filter="url(#soft)">
    <ellipse cx="60" cy="60" rx="55" ry="30" fill="white"/>
    <ellipse cx="120" cy="55" rx="50" ry="28" fill="white"/>
    <ellipse cx="160" cy="65" rx="35" ry="22" fill="white"/>
    <ellipse cx="90" cy="75" rx="65" ry="28" fill="white"/>
  </g>
</svg>
"""

# ================= CLOUDS (ALWAYS RUNNING) =================
for i in range(12):
    size = random.randint(140, 300)
    top = random.randint(30, 350)
    speed = random.choice(["back", "mid", "front"])
    delay = random.uniform(-150, 0)

    st.markdown(
        f"""
        <div class="cloud {speed}" 
             style="top:{top}px; width:{size}px; animation-delay:{delay}s;">
             {cloud_svg}
        </div>
        """,
        unsafe_allow_html=True
    )

# ================= WEATHER EFFECTS =================
if st.session_state.weather_condition:

    weather = st.session_state.weather_condition.lower()

    # ☀️ Sun
    if "clear" in weather:
        st.markdown('<div class="sun"></div>', unsafe_allow_html=True)

    # 🌧 Rain
    if "rain" in weather:
        for i in range(60):
            left = random.randint(0, 100)
            delay = random.uniform(0, 5)
            speed = random.uniform(0.5, 1.5)

            st.markdown(
                f"""
                <div class="rain"
                     style="
                        left:{left}%;
                        animation-duration:{speed}s;
                        animation-delay:{delay}s;
                     ">
                </div>
                """,
                unsafe_allow_html=True
            )

# ================= LOCATION =================
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            lat, lon = g.latlng
            url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
            data = requests.get(url).json()
            if data:
                city = data[0]["name"].lower()
                if city in ["hyderabad", ""]:
                    return "suryapet"
                return city
        return "suryapet"
    except:
        return "suryapet"

# ================= SESSION =================
if "city" not in st.session_state:
    st.session_state["city"] = detect_location()

# ================= INPUT =================
col1, col2 = st.columns([3,1])

with col1:
    st.text_input("Enter City", key="city")

with col2:
    if st.button("📍 Auto Detect"):
        st.session_state["city"] = detect_location()
        st.rerun()

city = st.session_state["city"].lower()

# ================= CITY FIX =================
city_alias = {
    "hyd": "hyderabad",
    "vizag": "visakhapatnam",
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "madras": "chennai",
    "delhi": "new delhi"
}

if city in city_alias:
    city = city_alias[city]
else:
    match = get_close_matches(city, city_alias.keys(), n=1, cutoff=0.7)
    if match:
        city = city_alias[match[0]]

# ================= WEATHER =================
if st.button("Get Weather"):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    if str(data.get("cod")) != "200":
        st.error("❌ City not found")
    else:
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        weather = data["weather"][0]["description"]

        # SAVE CONDITION (IMPORTANT)
        st.session_state.weather_condition = weather

        # ICON
        if "clear" in weather:
            icon = "☀️"
        elif "cloud" in weather:
            icon = "☁️"
        elif "rain" in weather:
            icon = "🌧"
        else:
            icon = "🌤"

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.success(f"📍 {city.title()}")
            st.markdown(f"# {icon} {temp}°C")
            st.metric("Feels Like", f"{feels} °C")
            st.metric("Humidity", f"{humidity}%")
            st.metric("Wind Speed", f"{wind} m/s")
            st.write(f"Condition: {weather.title()}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            lat = data["coord"]["lat"]
            lon = data["coord"]["lon"]
            st.map(pd.DataFrame({"lat":[lat], "lon":[lon]}))

        # ===== FORECAST =====
        st.subheader("📊 5-Day Forecast")

        forecast = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        ).json()

        temps, days = [], []
        for i in range(0, 40, 8):
            item = forecast["list"][i]
            temps.append(item["main"]["temp"])
            days.append(item["dt_txt"].split()[0])

        df = pd.DataFrame({"Day": days, "Temperature": temps})
        fig = px.line(df, x="Day", y="Temperature", markers=True)
        st.plotly_chart(fig, use_container_width=True)
