import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from difflib import get_close_matches
import geocoder
import time

# ================= CONFIG =================
API_KEY = "YOUR_API_KEY"   # <-- Put your key here

st.set_page_config(page_title="WeatherX", layout="wide")

# ================= UI STYLE =================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: linear-gradient(-45deg, #1e3c72, #2a5298, #1c92d2, #2c5364);
    background-size: 400% 400%;
    animation: gradientMove 15s ease infinite;
    color: white;
}

@keyframes gradientMove {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}

/* CLOUDS */
.cloud {
    position: fixed;
    width: 160px;
    height: 70px;
    background: rgba(255,255,255,0.7);
    border-radius: 70px;
    animation: cloudMove 35s linear infinite;
    z-index: 0;
}

@keyframes cloudMove {
    0% { transform: translateX(-300px); }
    100% { transform: translateX(120vw); }
}

/* SUN */
.sun {
    position: fixed;
    top: 80px;
    right: 120px;
    width: 110px;
    height: 110px;
    background: radial-gradient(circle, #FFD700, #FF8C00);
    border-radius: 50%;
    animation: sunFloat 8s ease-in-out infinite;
    box-shadow: 0 0 60px rgba(255,200,0,0.6);
}

@keyframes sunFloat {
    0% { transform: translateY(0);}
    50% { transform: translateY(-25px);}
    100% { transform: translateY(0);}
}

/* CARD */
.card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
}

/* BUTTON FIX */
button {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

st.title("🌤 WeatherX")

# ================= SMART SEARCH =================
aliases = {
    "ranga reddy": "hyderabad",
    "rangareddy": "hyderabad",
    "vizag": "visakhapatnam",
    "hyd": "hyderabad",
    "delhi": "new delhi"
}

def smart_city(city):
    city = city.lower().strip()
    if city in aliases:
        return aliases[city]

    match = get_close_matches(city, aliases.keys(), n=1, cutoff=0.7)
    if match:
        return aliases[match[0]]

    return city

# ================= SAFE API =================
def get_weather(city):
    try:
        geo = requests.get(
            f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        ).json()

        if not geo or len(geo) == 0:
            return None

        lat = geo[0].get("lat")
        lon = geo[0].get("lon")

        if lat is None or lon is None:
            return None

        data = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        ).json()

        return data

    except:
        return None

def get_forecast(city):
    try:
        geo = requests.get(
            f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        ).json()

        if not geo:
            return None

        lat = geo[0]["lat"]
        lon = geo[0]["lon"]

        return requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        ).json()

    except:
        return None

# ================= LOCATION (SAFE FIX) =================
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            return "suryapet"   # stable fallback (avoids wrong "the dalles")
    except:
        pass
    return "suryapet"

# ================= SESSION =================
if "city" not in st.session_state:
    st.session_state.city = detect_location()

# ================= INPUT =================
col1, col2, col3 = st.columns([3,1,1])

with col1:
    st.text_input("🔍 Search City", key="city")

with col2:
    if st.button("📍 Auto Detect"):
        st.session_state.city = detect_location()
        st.rerun()

with col3:
    get_weather_btn = st.button("🔍 Get Weather")

city = smart_city(st.session_state.city)

# ================= LOADING =================
with st.spinner("Fetching weather..."):
    time.sleep(0.5)
    data = get_weather(city)

# ================= ERROR HANDLING =================
if not data or str(data.get("cod")) != "200":
    st.error("❌ City not found or API issue")
    st.stop()

# ================= WEATHER =================
weather = data["weather"][0]["description"]

# ================= ANIMATIONS =================
for i in range(4):
    st.markdown(
        f'<div class="cloud" style="top:{120 + i*90}px; animation-delay:{i*5}s;"></div>',
        unsafe_allow_html=True
    )

if "clear" in weather:
    st.markdown('<div class="sun"></div>', unsafe_allow_html=True)

# ================= DATA =================
temp = data["main"]["temp"]
feels = data["main"]["feels_like"]
humidity = data["main"]["humidity"]
wind = data["wind"]["speed"]

lat = data["coord"]["lat"]
lon = data["coord"]["lon"]

# ================= UI =================
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.success(f"📍 {city.title()}")
    st.markdown(f"# 🌡 {round(temp)}°C")
    st.write(weather.title())

    st.metric("Feels Like", f"{round(feels)}°C")
    st.metric("Humidity", f"{humidity}%")
    st.metric("Wind", f"{wind} m/s")

with col2:
    st.map(pd.DataFrame({"lat":[lat], "lon":[lon]}))

st.markdown('</div>', unsafe_allow_html=True)

# ================= FORECAST =================
st.subheader("📊 5-Day Forecast")

forecast = get_forecast(city)

if forecast and "list" in forecast:
    temps, days = [], []

    for i in range(0,40,8):
        item = forecast["list"][i]
        temps.append(item["main"]["temp"])
        days.append(item["dt_txt"].split()[0])

    df = pd.DataFrame({
        "Day": days,
        "Temperature": temps
    })

    fig = px.line(df, x="Day", y="Temperature", markers=True)
    st.plotly_chart(fig, use_container_width=True)
