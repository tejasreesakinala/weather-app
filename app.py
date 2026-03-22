import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
import time

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="WeatherX", layout="wide")

# ================= UI STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Thin Divider */
hr {
    margin-top: 5px !important;
    margin-bottom: 5px !important;
    height: 1px !important;
    background: rgba(255,255,255,0.15) !important;
    border: none !important;
}

/* Glass Card */
.card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
}

/* Prevent animation overlap */
.block-container {
    position: relative;
    z-index: 1;
}

/* SUN */
.sun {
    position: absolute;
    top: 60px;
    left: 70%;
    width: 90px;
    height: 90px;
    background: radial-gradient(circle, yellow, orange);
    border-radius: 50%;
    animation: sunMove 10s infinite ease-in-out;
}
@keyframes sunMove {
    0% { transform: translateY(0) translateX(0);}
    50% { transform: translateY(-25px) translateX(20px);}
    100% { transform: translateY(0) translateX(0);}
}

/* CLOUD (FIXED PREMIUM) */
.cloud {
    position: absolute;
    width: 120px;
    height: 50px;
    background: rgba(255,255,255,0.85);
    border-radius: 50px;
    animation: moveClouds 40s linear infinite;
    z-index: 0;
    filter: blur(2px);
}

.cloud::before {
    content:'';
    position:absolute;
    top:-20px;
    left:20px;
    width:70px;
    height:70px;
    background: rgba(255,255,255,0.85);
    border-radius:50%;
}

.cloud::after {
    content:'';
    position:absolute;
    top:-10px;
    left:60px;
    width:50px;
    height:50px;
    background: rgba(255,255,255,0.85);
    border-radius:50%;
}

@keyframes moveClouds {
    0% { left: -150px; }
    100% { left: 110%; }
}

/* RAIN */
.rain {
    position:absolute;
    width:2px;
    height:20px;
    background:lightblue;
    animation: rainFall 0.5s linear infinite;
}
@keyframes rainFall {
    0% { transform: translateY(0);}
    100% { transform: translateY(600px);}
}

/* LIGHTNING */
.lightning {
    position:absolute;
    width:100%;
    height:100%;
    animation: lightning 4s infinite;
}
@keyframes lightning {
    0% {background:transparent;}
    50% {background:white;}
    100% {background:transparent;}
}
</style>
""", unsafe_allow_html=True)

st.title("🌤 WeatherX")

# ================= FUNCTIONS =================
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
                if city in ["hyderabad", "the dalles", ""]:
                    return "suryapet"
                return city
    except:
        pass
    return "suryapet"

# ================= SESSION =================
if "city" not in st.session_state:
    st.session_state["city"] = detect_location()

if "auto_trigger" not in st.session_state:
    st.session_state["auto_trigger"] = False

if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

# ================= AUTO DETECT FIX =================
if st.session_state["auto_trigger"]:
    st.session_state["city"] = detect_location()
    st.session_state["auto_trigger"] = False

# ================= INPUT =================
col1, col2, col3 = st.columns([3,1,1])

with col1:
    st.text_input("🔍 Search City", key="city")

with col2:
    if st.button("📍 Auto Detect"):
        st.session_state["auto_trigger"] = True
        st.rerun()

with col3:
    get_btn = st.button("🔍 Get Weather")

city = st.session_state["city"].lower()

# ================= WEATHER =================
if get_btn:
    with st.spinner("Loading weather..."):
        time.sleep(1)
        data = get_weather(city)
else:
    data = get_weather(city)

if not data or str(data.get("cod")) != "200":
    st.error("❌ Location not found")
else:
    weather = data["weather"][0]["description"]

    # ================= ANIMATION =================
    if "clear" in weather:
        st.markdown('<div class="sun"></div>', unsafe_allow_html=True)
        for i in range(4):
            st.markdown(
                f'<div class="cloud" style="top:{80 + i*60}px; animation-delay:{i*6}s;"></div>',
                unsafe_allow_html=True
            )

    elif "cloud" in weather:
        for i in range(4):
            st.markdown(
                f'<div class="cloud" style="top:{80 + i*60}px; animation-delay:{i*6}s;"></div>',
                unsafe_allow_html=True
            )

    elif "rain" in weather:
        for i in range(40):
            st.markdown(
                f'<div class="rain" style="left:{i*25}px;"></div>',
                unsafe_allow_html=True
            )

    elif "storm" in weather:
        st.markdown('<div class="lightning"></div>', unsafe_allow_html=True)

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
            if city not in st.session_state["favorites"]:
                st.session_state["favorites"].append(city)

    with col2:
        if st.session_state["favorites"]:
            selected = st.selectbox("⭐ Favorites", st.session_state["favorites"])
            st.session_state["city"] = selected
            st.rerun()

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

    if forecast and "list" in forecast:
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
