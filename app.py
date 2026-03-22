import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
import time

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="WeatherX", layout="wide")

# ================= BACKGROUND =================
def get_background_style(weather):
    weather = weather.lower()

    if "clear" in weather:
        return """
        <style>
        .stApp {
            background: linear-gradient(-45deg, #ffb347, #ffcc33, #ff9a00, #ffb347);
            background-size: 400% 400%;
            animation: gradient 10s ease infinite;
            color: #1a1a1a;
        }

        h1, h2, h3, p, label {
            color: #1a1a1a !important;
        }

        .stTextInput input {
            background: rgba(0,0,0,0.7);
            color: white;
        }

        .stButton button {
            background: black;
            color: white;
            border-radius: 10px;
        }
        </style>
        """

    elif "cloud" in weather:
        return """
        <style>
        .stApp {
            background: linear-gradient(-45deg, #bdc3c7, #2c3e50);
            background-size: 400% 400%;
            animation: gradient 12s ease infinite;
        }
        </style>
        """

    elif "rain" in weather:
        return """
        <style>
        .stApp {
            background: linear-gradient(-45deg, #000428, #004e92);
            background-size: 400% 400%;
            animation: gradient 8s ease infinite;
        }
        </style>
        """

    else:
        return """
        <style>
        .stApp {
            background: linear-gradient(-45deg, #0f2027, #203a43);
            background-size: 400% 400%;
            animation: gradient 12s ease infinite;
        }
        </style>
        """

# ================= GLOBAL STYLE =================
st.markdown("""
<style>

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Clean divider */
hr {
    margin: 5px 0;
    height: 1px;
    background: rgba(255,255,255,0.2);
    border: none;
}

/* Remove empty space */
div[data-testid="stVerticalBlock"] > div:empty {
    display: none;
}

/* Glass card */
.card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}

/* Layer fix */
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
    animation: sunMove 8s infinite ease-in-out;
}

@keyframes sunMove {
    0% {transform: translateY(0);}
    50% {transform: translateY(-20px);}
    100% {transform: translateY(0);}
}

/* CLOUD */
.cloud {
    position: absolute;
    width: 120px;
    height: 50px;
    background: rgba(255,255,255,0.9);
    border-radius: 50px;
    animation: moveClouds 45s linear infinite;
    opacity: 0.9;
}

.cloud::before {
    content:'';
    position:absolute;
    top:-20px;
    left:20px;
    width:70px;
    height:70px;
    background:white;
    border-radius:50%;
}

.cloud::after {
    content:'';
    position:absolute;
    top:-10px;
    left:60px;
    width:50px;
    height:50px;
    background:white;
    border-radius:50%;
}

@keyframes moveClouds {
    0% { left: -200px; }
    100% { left: 110%; }
}

</style>
""", unsafe_allow_html=True)

st.title("🌤 WeatherX")

# ================= FUNCTIONS =================
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            lat, lon = g.latlng
            data = requests.get(
                f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
            ).json()

            if data:
                return data[0]["name"].lower()
    except:
        pass
    return "suryapet"

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

city = st.session_state.city.lower()

# ================= WEATHER =================
if get_btn:
    with st.spinner("Loading weather..."):
        time.sleep(1)
        data = get_weather(city)
else:
    data = get_weather(city)

if not data:
    st.error("❌ City not found")
else:
    weather = data["weather"][0]["description"]
    st.markdown(get_background_style(weather), unsafe_allow_html=True)

    # ANIMATION
    if "clear" in weather:
        st.markdown('<div class="sun"></div>', unsafe_allow_html=True)

    for i in range(4):
        st.markdown(
            f'<div class="cloud" style="top:{120 + i*70}px; animation-delay:{i*5}s;"></div>',
            unsafe_allow_html=True
        )

    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]

    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2,1])

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

    # FORECAST
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
        
