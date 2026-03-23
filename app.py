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
/* ================= DYNAMIC BACKGROUND ================= */
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

/* ================= CLOUD SYSTEM ================= */

/* Back clouds (slow) */
.cloud-back {
    position: fixed;
    top: 100px;
    width: 200px;
    height: 80px;
    background: rgba(255,255,255,0.25);
    border-radius: 80px;
    animation: moveCloudsSlow 90s linear infinite;
    filter: blur(3px);
    z-index: 0;
}

/* Front clouds (fast) */
.cloud-front {
    position: fixed;
    top: 200px;
    width: 140px;
    height: 60px;
    background: rgba(255,255,255,0.6);
    border-radius: 60px;
    animation: moveCloudsFast 40s linear infinite;
    z-index: 0;
}

@keyframes moveCloudsSlow {
    0% { transform: translateX(-300px); }
    100% { transform: translateX(120vw); }
}

@keyframes moveCloudsFast {
    0% { transform: translateX(-200px); }
    100% { transform: translateX(120vw); }
}

/* ================= SUN ================= */
.sun {
    position: fixed;
    top: 80px;
    left: 70%;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, #ffd700, #ff8c00);
    border-radius: 50%;
    animation: sunFloat 10s ease-in-out infinite;
    box-shadow: 0 0 60px rgba(255, 200, 0, 0.6);
    z-index: 0;
}

@keyframes sunFloat {
    0% { transform: translateY(0); }
    50% { transform: translateY(-25px); }
    100% { transform: translateY(0); }
}
<style>
""",unsafe_allow_html=True
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
   # ================= NEW SMOOTH ANIMATION =================

# BACK CLOUDS (slow - depth effect)
for i in range(3):
    st.markdown(
        f'<div class="cloud-back" style="top:{100 + i*120}px; animation-delay:{i*20}s;"></div>',
        unsafe_allow_html=True
    )

# FRONT CLOUDS (faster - realistic movement)
for i in range(4):
    st.markdown(
        f'<div class="cloud-front" style="top:{150 + i*70}px; animation-delay:{i*8}s;"></div>',
        unsafe_allow_html=True
    )

# SUN (only for clear sky)
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
