import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
from difflib import get_close_matches
import random

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="Weather Pro", layout="wide")

# ================= UI + CSS =================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1c92d2);
    background-size: 400% 400%;
    animation: gradient 12s ease infinite;
    color: white;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* CARD */
.card {
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(12px);
}

/* CLOUD SYSTEM */
.cloud {
    position: fixed;
    pointer-events: none;
    animation: cloudMove linear infinite;
    z-index: 0;
}

.cloud.back {
    animation-duration: 160s;
    opacity: 0.25;
}

.cloud.mid {
    animation-duration: 90s;
    opacity: 0.5;
}

.cloud.front {
    animation-duration: 50s;
    opacity: 0.85;
}

@keyframes cloudMove {
    from { transform: translateX(-150vw); }
    to { transform: translateX(120vw); }
}

/* SUN */
.sun {
    position: fixed;
    top: 80px;
    right: 100px;
    width: 90px;
    height: 90px;
    background: radial-gradient(circle, #FFD700, #FF8C00);
    border-radius: 50%;
    animation: sunMove 8s ease-in-out infinite;
    box-shadow: 0 0 50px rgba(255,200,0,0.6);
}

@keyframes sunMove {
    0% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
    100% { transform: translateY(0); }
}

.block-container {
    position: relative;
    z-index: 1;
}

</style>
""", unsafe_allow_html=True)

st.title("🌤 Weather Pro Dashboard")

# ================= CLOUD SHAPE (REALISTIC) =================
cloud_svg = """
<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="blur">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
  </defs>
  <g filter="url(#blur)">
    <ellipse cx="60" cy="60" rx="50" ry="30" fill="white"/>
    <ellipse cx="110" cy="55" rx="45" ry="28" fill="white"/>
    <ellipse cx="150" cy="65" rx="35" ry="25" fill="white"/>
    <ellipse cx="90" cy="75" rx="65" ry="28" fill="white"/>
  </g>
</svg>
"""

# ================= CLOUD GENERATION (RUN ALWAYS) =================
for i in range(10):
    size = random.randint(140, 280)
    top = random.randint(40, 320)
    speed_type = random.choice(["back", "mid", "front"])
    delay = random.uniform(-150, 0)

    st.markdown(
        f"""
        <div class="cloud {speed_type}" 
             style="top:{top}px; width:{size}px; animation-delay:{delay}s;">
             {cloud_svg}
        </div>
        """,
        unsafe_allow_html=True
    )

# ================= LOCATION DETECT =================
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            lat, lon = g.latlng
            url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
            data = requests.get(url).json()

            if data:
                city = data[0]["name"].lower()
                if city in ["hyderabad", "the dalles", ""]:
                    return "suryapet"
                return city
        return "suryapet"
    except:
        return "suryapet"

# ================= SESSION =================
if "city" not in st.session_state:
    st.session_state["city"] = detect_location()

if "auto_detect" not in st.session_state:
    st.session_state["auto_detect"] = False

if st.session_state["auto_detect"]:
    st.session_state["city"] = detect_location()
    st.session_state["auto_detect"] = False

# ================= INPUT =================
col1, col2 = st.columns([3,1])

with col1:
    st.text_input("Enter City", key="city")

with col2:
    st.write("")
    if st.button("📍 Auto Detect"):
        st.session_state["auto_detect"] = True
        st.rerun()

city = st.session_state["city"].lower()

# ================= ALIASES =================
city_alias = {
    "ranga reddy": "hyderabad",
    "rangareddy": "hyderabad",
    "medchal": "hyderabad",
    "sangareddy": "hyderabad",
    "vizag": "visakhapatnam",
    "hyd": "hyderabad",
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "madras": "chennai",
    "calcutta": "kolkata",
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

        # SUN
        if "clear" in weather:
            st.markdown('<div class="sun"></div>', unsafe_allow_html=True)

        # ICON
        if "clear" in weather:
            icon = "☀️"
        elif "cloud" in weather:
            icon = "☁️"
        elif "rain" in weather:
            icon = "🌧"
        elif "storm" in weather:
            icon = "⛈"
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
            df = pd.DataFrame({"lat":[lat], "lon":[lon]})
            st.map(df)

        st.subheader("📊 5-Day Forecast")

        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        forecast_data = requests.get(forecast_url).json()

        temps, days = [], []
        for i in range(0,40,8):
            item = forecast_data["list"][i]
            temps.append(item["main"]["temp"])
            days.append(item["dt_txt"].split()[0])

        df_chart = pd.DataFrame({"Day": days, "Temperature": temps})
        fig = px.line(df_chart, x="Day", y="Temperature", markers=True)
        st.plotly_chart(fig, use_container_width=True)
