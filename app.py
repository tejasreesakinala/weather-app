import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
from difflib import get_close_matches

API_KEY = "YOUR_API_KEY"

st.set_page_config(page_title="WeatherX", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #1e3c72, #2a5298, #1c92d2);
    background-size: 400% 400%;
    animation: gradientMove 12s ease infinite;
    color: white;
}
@keyframes gradientMove {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}

.cloud {
    position: fixed;
    width: 140px;
    height: 60px;
    background: rgba(255,255,255,0.6);
    border-radius: 60px;
    animation: cloudMove 40s linear infinite;
}
@keyframes cloudMove {
    0% {transform: translateX(-200px);}
    100% {transform: translateX(120vw);}
}

.sun {
    position: fixed;
    top: 80px;
    left: 70%;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, yellow, orange);
    border-radius: 50%;
    animation: sunMove 8s infinite ease-in-out;
}
@keyframes sunMove {
    0% {transform: translateY(0);}
    50% {transform: translateY(-20px);}
    100% {transform: translateY(0);}
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
aliases = {
    "ranga reddy": "hyderabad",
    "rangareddy": "hyderabad",
    "vizag": "visakhapatnam",
    "hyd": "hyderabad",
    "delhi": "new delhi"
}

def smart_city(city):
    city = city.lower()
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

        if not geo:
            return None

        lat = geo[0].get("lat")
        lon = geo[0].get("lon")

        if lat is None:
            return None

        return requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        ).json()

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

# ================= LOCATION =================
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            return "suryapet"   # forcing stable
    except:
        pass
    return "suryapet"

# ================= SESSION =================
if "city" not in st.session_state:
    st.session_state.city = detect_location()

# ================= INPUT =================
col1, col2, col3 = st.columns([3,1,1])

with col1:
    st.text_input("Search City", key="city")

with col2:
    if st.button("📍 Auto Detect"):
        st.session_state.city = detect_location()
        st.rerun()

with col3:
    get_btn = st.button("Get Weather")

city = smart_city(st.session_state.city)

# ================= DATA =================
data = get_weather(city)

if not data or str(data.get("cod")) != "200":
    st.error("City not found")
else:
    weather = data["weather"][0]["description"]

    # ================= ANIMATION =================
    for i in range(3):
        st.markdown(f'<div class="cloud" style="top:{120+i*80}px;"></div>', unsafe_allow_html=True)

    if "clear" in weather:
        st.markdown('<div class="sun"></div>', unsafe_allow_html=True)

    # ================= UI =================
    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.success(city.title())
        st.markdown(f"# {temp}°C")
        st.write(weather.title())
        st.metric("Feels Like", f"{feels}°C")
        st.metric("Humidity", f"{humidity}%")
        st.metric("Wind", f"{wind} m/s")

    with col2:
        st.map(pd.DataFrame({"lat":[lat], "lon":[lon]}))

    st.markdown('</div>', unsafe_allow_html=True)

    # ================= FORECAST =================
    forecast = get_forecast(city)

    if forecast:
        temps, days = [], []
        for i in range(0,40,8):
            item = forecast["list"][i]
            temps.append(item["main"]["temp"])
            days.append(item["dt_txt"].split()[0])

        df = pd.DataFrame({"Day": days, "Temp": temps})
        fig = px.line(df, x="Day", y="Temp", markers=True)
        st.plotly_chart(fig, use_container_width=True)
