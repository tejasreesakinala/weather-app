import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="WeatherX", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Keep UI above animation */
.block-container {
    position: relative;
    z-index: 2;
}

/* CLOUDS (BEHIND UI) */
.cloud {
    position: fixed;
    width: 140px;
    height: 60px;
    background: rgba(255,255,255,0.7);
    border-radius: 60px;
    animation: moveClouds 60s linear infinite;
    opacity: 0.6;
    z-index: 0;
}

@keyframes moveClouds {
    0% { transform: translateX(-200px); }
    100% { transform: translateX(120vw); }
}

/* SUN */
.sun {
    position: fixed;
    top: 60px;
    left: 65%;
    width: 90px;
    height: 90px;
    background: radial-gradient(circle, yellow, orange);
    border-radius: 50%;
    animation: sunMove 8s infinite ease-in-out;
    z-index: 0;
}

@keyframes sunMove {
    0% { transform: translate(0,0);}
    50% { transform: translate(50px,-30px);}
    100% { transform: translate(0,0);}
}

/* Glass card */
.card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
}
</style>
""", unsafe_allow_html=True)

st.title("🌤 WeatherX")

# ================= GPS DETECTION =================
def detect_location_gps():
    try:
        # using ipinfo fallback if GPS not triggered
        res = requests.get("https://ipinfo.io/json").json()
        return res.get("city", "suryapet").lower()
    except:
        return "suryapet"

# ================= WEATHER =================
@st.cache_data(ttl=300)
def get_weather(city):
    geo = requests.get(
        f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    ).json()

    if not geo:
        return None

    lat, lon = geo[0]["lat"], geo[0]["lon"]

    return requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    ).json()

@st.cache_data(ttl=300)
def get_forecast(city):
    geo = requests.get(
        f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    ).json()

    if not geo:
        return None

    lat, lon = geo[0]["lat"], geo[0]["lon"]

    return requests.get(
        f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    ).json()

# ================= SESSION =================
if "city" not in st.session_state:
    st.session_state["city"] = "suryapet"

# ================= INPUT =================
col1, col2, col3 = st.columns([3,1,1])

with col1:
    st.text_input("🔍 Search City", key="city")

with col2:
    if st.button("📍 Auto Detect (GPS)"):
        st.session_state["city"] = detect_location_gps()
        st.rerun()

with col3:
    get_btn = st.button("🔍 Get Weather")

city = st.session_state["city"].lower()

# ================= WEATHER =================
if get_btn:
    with st.spinner("Fetching real-time weather..."):
        time.sleep(1)
        data = get_weather(city)
else:
    data = get_weather(city)

if not data:
    st.error("❌ City not found")
else:
    weather = data["weather"][0]["description"]

    # ================= ANIMATION =================
    if "clear" in weather:
        st.markdown('<div class="sun"></div>', unsafe_allow_html=True)

    for i in range(6):
        st.markdown(
            f'<div class="cloud" style="top:{80 + i*70}px; animation-delay:{i*8}s;"></div>',
            unsafe_allow_html=True
        )

    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])

    with col1:
        st.success(f"📍 {city.title()}")
        st.markdown(f"# 🌡 {temp}°C")
        st.write(weather.title())
        st.metric("Feels Like", f"{feels}°C")
        st.metric("Humidity", f"{humidity}%")
        st.metric("Wind", f"{wind} m/s")

    with col2:
        df = pd.DataFrame({"lat":[lat], "lon":[lon]})
        st.map(df)

    st.markdown('</div>', unsafe_allow_html=True)

    # ================= FORECAST =================
    st.subheader("📊 5-Day Forecast")

    forecast = get_forecast(city)

    if forecast:
        temps, days = [], []

        for i in range(0,40,8):
            item = forecast["list"][i]
            temps.append(item["main"]["temp"])
            days.append(item["dt_txt"].split()[0])

        df_chart = pd.DataFrame({"Day": days, "Temperature": temps})

        fig = px.line(df_chart, x="Day", y="Temperature", markers=True)
        st.plotly_chart(fig, use_container_width=True)
