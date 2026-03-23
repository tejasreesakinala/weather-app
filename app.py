import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
from datetime import datetime
import random
from difflib import get_close_matches

# ================= CONFIG =================
API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"
st.set_page_config(page_title="Weather Pro Ultimate", layout="wide", page_icon="🌤")

# ================= SESSION =================
if "city_input" not in st.session_state:
    st.session_state.city_input = "Suryapet"
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

# ================= SMART CITY SYSTEM =================
city_alias = {
    "vizag": "visakhapatnam",
    "vishakapatnam": "visakhapatnam",
    "ranga reddy": "hyderabad",
    "rangareddy": "hyderabad",
    "hyd": "hyderabad",
    "secunderabad": "hyderabad",
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "madras": "chennai",
    "calcutta": "kolkata",
    "delhi": "new delhi"
}

def normalize_city(city):
    city = city.lower().strip()
    if city in city_alias:
        return city_alias[city]
    match = get_close_matches(city, city_alias.keys(), n=1, cutoff=0.7)
    if match:
        return city_alias[match[0]]
    return city

# ================= GET WEATHER =================
def get_weather(city):
    city = normalize_city(city)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()
    return res if res.get("cod") == 200 else None

def get_forecast(city):
    city = normalize_city(city)
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

# ================= DYNAMIC BACKGROUND =================
def get_bg(hour):
    if 6 <= hour < 12:
        return "#4facfe, #00f2fe"      # Morning
    elif 12 <= hour < 17:
        return "#43cea2, #185a9d"      # Afternoon
    elif 17 <= hour < 20:
        return "#ff7e5f, #feb47b"      # Sunset
    else:
        return "#0f2027, #203a43, #2c5364"  # Night

current_hour = datetime.now().hour
bg_gradient = get_bg(current_hour)

# ================= CSS =================
st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(-45deg, {bg_gradient});
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    color: white;
}}

@keyframes gradient {{
    0% {{background-position: 0% 50%;}}
    50% {{background-position: 100% 50%;}}
    100% {{background-position: 0% 50%;}}
}}

.weather-card {{
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(15px);
    border-radius: 25px;
    padding: 25px;
}}

.cloud {{
    position: fixed;
    width: 180px;
    height: 60px;
    background:
        radial-gradient(circle at 30% 50%, white 40%, transparent 70%),
        radial-gradient(circle at 60% 40%, white 35%, transparent 70%),
        radial-gradient(circle at 80% 60%, white 30%, transparent 70%);
    filter: blur(10px);
    opacity: 0.4;
    animation: move linear infinite;
    border-radius: 50px;
}}

@keyframes move {{
    from {{ transform: translateX(-120vw); }}
    to {{ transform: translateX(120vw); }}
}}

.sun {{
    position: fixed;
    top: 60px;
    right: 80px;
    width: 140px;
    height: 140px;
    background: radial-gradient(circle, #FFD54F 0%, transparent 70%);
    filter: blur(10px);
}}

.moon {{
    position: fixed;
    top: 60px;
    right: 80px;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, #fff 0%, transparent 70%);
    filter: blur(5px);
}}

.rain {{
    position: fixed;
    width: 2px;
    height: 20px;
    background: rgba(255,255,255,0.5);
    animation: fall linear infinite;
}}

@keyframes fall {{
    from {{ transform: translateY(-100px); }}
    to {{ transform: translateY(110vh); }}
}}

.block-container {{
    position: relative;
    z-index: 10;
}}
</style>
""", unsafe_allow_html=True)

st.title("🌤 Weather Pro Ultimate")

# ================= CLOUDS ALWAYS =================
for i in range(10):
    st.markdown(f"""
    <div class="cloud" style="
        top:{random.randint(50,300)}px;
        animation-duration:{random.randint(40,100)}s;
        animation-delay:{random.uniform(-100,0)}s;">
    </div>
    """, unsafe_allow_html=True)

# ================= INPUT =================
col1, col2 = st.columns([4,1])

with col1:
    st.text_input("Search City", key="city_input")
    city = st.session_state.city_input

with col2:
    st.write("")
    if st.button("📍 Auto Detect"):
        try:
            g = geocoder.ipinfo('me')
            if g.city:
                st.session_state.city_input = g.city
            else:
                st.session_state.city_input = "Suryapet"
        except:
            st.session_state.city_input = "Suryapet"
        st.rerun()

# ================= FETCH =================
if city:
    data = get_weather(city)
    if data:
        st.session_state.weather_data = data
    else:
        st.error("❌ City not found")

# ================= EFFECTS =================
if st.session_state.weather_data:
    w = st.session_state.weather_data
    condition = w["weather"][0]["main"].lower()

    if "clear" in condition:
        if 6 <= current_hour < 18:
            st.markdown('<div class="sun"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="moon"></div>', unsafe_allow_html=True)

    if "rain" in condition:
        for i in range(50):
            st.markdown(f"""
            <div class="rain" style="
                left:{random.randint(0,100)}%;
                animation-duration:{random.uniform(0.5,1.2)}s;">
            </div>
            """, unsafe_allow_html=True)

# ================= DISPLAY =================
if st.session_state.weather_data:
    w = st.session_state.weather_data

    col1, col2 = st.columns([2,2])

    with col1:
        st.markdown(f"""
        <div class="weather-card">
            <h2>{w['name']}</h2>
            <h1>{round(w['main']['temp'])}°C</h1>
            <p>{w['weather'][0]['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Humidity", f"{w['main']['humidity']}%")
        m2.metric("Wind", f"{w['wind']['speed']} m/s")
        m3.metric("Feels", f"{round(w['main']['feels_like'])}°C")

    with col2:
        st.map(pd.DataFrame({
            "lat":[w['coord']['lat']],
            "lon":[w['coord']['lon']]
        }))

    # ===== FORECAST =====
    st.subheader("📊 Forecast")
    forecast = get_forecast(w["name"])

    if forecast.get("cod") == "200":
        df = pd.DataFrame([
            {"Time": i["dt_txt"], "Temp": i["main"]["temp"]}
            for i in forecast["list"]
        ])

        fig = px.line(df, x="Time", y="Temp", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
