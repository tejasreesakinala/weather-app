import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
from difflib import get_close_matches

API_KEY = "YOUR_API_KEY_HERE"

st.set_page_config(page_title="WeatherX", layout="wide")

# ================= CSS =================
st.markdown("""
<style>

/* DYNAMIC BACKGROUND */
.stApp {
    background: linear-gradient(-45deg, #1e3c72, #2a5298, #1c92d2, #2c5364);
    background-size: 400% 400%;
    animation: gradientMove 15s ease infinite;
    color: white;
}

@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* CLOUDS */
.cloud-back {
    position: fixed;
    width: 220px;
    height: 90px;
    background: rgba(255,255,255,0.2);
    border-radius: 100px;
    animation: moveCloudsSlow 80s linear infinite;
    filter: blur(3px);
}

.cloud-front {
    position: fixed;
    width: 150px;
    height: 70px;
    background: rgba(255,255,255,0.6);
    border-radius: 70px;
    animation: moveCloudsFast 40s linear infinite;
}

@keyframes moveCloudsSlow {
    0% { transform: translateX(-300px); }
    100% { transform: translateX(120vw); }
}

@keyframes moveCloudsFast {
    0% { transform: translateX(-200px); }
    100% { transform: translateX(120vw); }
}

/* SUN */
.sun {
    position: fixed;
    top: 80px;
    left: 70%;
    width: 110px;
    height: 110px;
    background: radial-gradient(circle, #ffd700, #ff8c00);
    border-radius: 50%;
    animation: sunMove 8s ease-in-out infinite;
}

@keyframes sunMove {
    0% { transform: translateY(0) translateX(0); }
    50% { transform: translateY(-30px) translateX(20px); }
    100% { transform: translateY(0) translateX(0); }
}

/* UI FIX */
.stButton>button {
    background: rgba(0,0,0,0.6);
    color: white;
    border-radius: 10px;
}

.stTextInput input {
    background: rgba(0,0,0,0.5);
    color: white;
}

.card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
}

</style>
""", unsafe_allow_html=True)

st.title("🌤 WeatherX")

# ================= SMART SEARCH =================
city_alias = {
    "ranga reddy": "hyderabad",
    "rangareddy": "hyderabad",
    "vizag": "visakhapatnam",
    "hyd": "hyderabad",
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "madras": "chennai",
    "calcutta": "kolkata",
    "delhi": "new delhi"
}

def smart_city(city):
    city = city.lower()
    if city in city_alias:
        return city_alias[city]
    match = get_close_matches(city, city_alias.keys(), n=1, cutoff=0.7)
    if match:
        return city_alias[match[0]]
    return city

# ================= LOCATION =================
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            lat, lon = g.latlng
            data = requests.get(
                f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
            ).json()

            if data:
                city = data[0]["name"].lower()
                if city in ["the dalles", ""]:
                    return "suryapet"
                return city
    except:
        pass
    return "suryapet"

# ================= API =================
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
    st.session_state.city = detect_location()

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ================= INPUT =================
col1, col2, col3 = st.columns([3,1,1])

with col1:
    st.text_input("🔍 Search City", key="city")

with col2:
    if st.button("📍 Auto Detect"):
        st.session_state.city = detect_location()
        st.rerun()

with col3:
    get_btn = st.button("🔍 Get Weather")

city = smart_city(st.session_state.city)

# ================= WEATHER =================
data = get_weather(city)

if not data or str(data.get("cod")) != "200":
    st.error("❌ Location not found")
else:
    weather = data["weather"][0]["description"]

    # ================= ANIMATION =================
    for i in range(3):
        st.markdown(f'<div class="cloud-back" style="top:{100+i*120}px;"></div>', unsafe_allow_html=True)

    for i in range(4):
        st.markdown(f'<div class="cloud-front" style="top:{150+i*70}px;"></div>', unsafe_allow_html=True)

    if "clear" in weather:
        st.markdown('<div class="sun"></div>', unsafe_allow_html=True)

    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]

    # ================= FAVORITES =================
    col1, col2 = st.columns([3,1])

    with col1:
        if st.button("⭐ Add to Favorites"):
            if city not in st.session_state.favorites:
                st.session_state.favorites.append(city)

    with col2:
        if st.session_state.favorites:
            selected = st.selectbox("⭐ Favorites", st.session_state.favorites)
            st.session_state.city = selected
            st.rerun()

    # ================= UI =================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

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

        df_chart = pd.DataFrame({
            "Day": days,
            "Temperature": temps
        })

        fig = px.line(df_chart, x="Day", y="Temperature", markers=True)
        st.plotly_chart(fig, use_container_width=True)
