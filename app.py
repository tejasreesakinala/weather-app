import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
from datetime import datetime
import random
from difflib import get_close_matches

# ================= CONFIG =================
# Note: In a production app, use st.secrets for the API key
API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"
st.set_page_config(page_title="Weather Pro Advanced", layout="wide", page_icon="🌤")

# ================= SESSION STATE =================
if "city_input" not in st.session_state:
    st.session_state.city_input = "Suryapet"

# ================= SMART CITY FIX =================
city_alias = {
    "vizag": "visakhapatnam",
    "vishakapatnam": "visakhapatnam",
    "rangareddy": "hyderabad",
    "ranga reddy": "hyderabad",
    "hyd": "hyderabad",
    "secunderabad": "hyderabad",
    "bangalore": "bengaluru",
    "bombay": "mumbai"
}

def normalize_city(city):
    city = city.lower().strip()
    if city in city_alias:
        return city_alias[city]
    match = get_close_matches(city, city_alias.keys(), n=1, cutoff=0.7)
    if match:
        return city_alias[match[0]]
    return city

# ================= ADVANCED CSS =================
st.markdown("""
<style>
/* Global styles */
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    color: white;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Glassmorphism Card */
.weather-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border-radius: 25px;
    padding: 30px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    margin-bottom: 20px;
}

/* IMPORTANT: Prevent animations from blocking clicks */
.cloud, .sun, .rain {
    pointer-events: none;
    z-index: 0;
}

/* CLOUD ANIMATION */
.cloud {
    position: fixed;
    width: 200px;
    height: 60px;
    background: white;
    filter: blur(25px);
    opacity: 0.3;
    animation: move linear infinite;
    border-radius: 50px;
}
@keyframes move {
    from { transform: translateX(-120vw); }
    to { transform: translateX(120vw); }
}

/* SUN PULSE */
.sun {
    position: fixed;
    top: 50px;
    right: 80px;
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, #FFD54F 0%, rgba(255,213,79,0.3) 60%, transparent 80%);
    filter: blur(15px);
    animation: pulse 4s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 0.4; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.1); }
}

/* RAIN FALL */
.rain {
    position: fixed;
    width: 2px;
    height: 20px;
    background: rgba(255,255,255,0.4);
    animation: fall linear infinite;
}
@keyframes fall {
    from { transform: translateY(-100px); }
    to { transform: translateY(110vh); }
}

.block-container { z-index: 10; position: relative; }
</style>
""", unsafe_allow_html=True)

# ================= BACKGROUND ELEMENTS =================
# Ambient Clouds (Always present)
for i in range(6):
    st.markdown(f'<div class="cloud" style="top:{random.randint(5, 35)}%; animation-duration:{random.randint(60, 120)}s; animation-delay:{random.randint(-100, 0)}s;"></div>', unsafe_allow_html=True)

# ================= HELPER FUNCTIONS =================
def get_weather(city):
    city = normalize_city(city)
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()
        return res if res.get("cod") == 200 else None
    except:
        return None

def get_forecast(city):
    city = normalize_city(city)
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()
        return res if res.get("cod") == "200" else None
    except:
        return None

# ================= UI LAYOUT =================
st.title("🌤️ Weather Pro Advanced")

col_input, col_btn = st.columns([4, 1])

with col_input:
    # Use session state to handle the value properly
    city_input = st.text_input("Search City", value=st.session_state.city_input)

with col_btn:
    st.write("##") # Alignment spacer
    if st.button("📍 Auto-Locate"):
        g = geocoder.ip('me')
        if g.city:
            st.session_state.city_input = g.city
            st.rerun()

# ================= DATA PROCESSING =================
if city_input:
    data = get_weather(city_input)
    
    if data:
        # 1. Trigger Weather Effects
        condition = data['weather'][0]['main'].lower()
        if "clear" in condition:
            st.markdown('<div class="sun"></div>', unsafe_allow_html=True)
        if "rain" in condition or "drizzle" in condition:
            for _ in range(60):
                st.markdown(f'<div class="rain" style="left:{random.randint(0,100)}%; animation-duration:{random.uniform(0.6,1.2)}s; animation-delay:{random.uniform(0,2)}s;"></div>', unsafe_allow_html=True)

        # 2. Main Display
        col_info, col_map = st.columns([3, 2])
        
        with col_info:
            # Weather Icon Selection
            icon_map = {"Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️"}
            weather_main = data['weather'][0]['main']
            display_icon = icon_map.get(weather_main, "🌤️")

            st.markdown(f"""
            <div class="weather-card">
                <h3 style='margin:0; opacity:0.8;'>{datetime.now().strftime('%A, %d %B')}</h3>
                <h1 style='font-size: 3.5rem; margin: 10px 0;'>{data['name']} {display_icon}</h1>
                <h2 style='font-size: 4rem; color: #ffeb3b; margin: 0;'>{round(data['main']['temp'])}°C</h2>
                <p style='font-size: 1.5rem; text-transform: capitalize;'>{data['weather'][0]['description']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Humidity", f"{data['main']['humidity']}%")
            m2.metric("Wind Speed", f"{data['wind']['speed']} m/s")
            m3.metric("Feels Like", f"{round(data['main']['feels_like'])}°C")

        with col_map:
            # Interactive Map
            map_df = pd.DataFrame({"lat": [data['coord']['lat']], "lon": [data['coord']['lon']]})
            st.map(map_df, zoom=10, use_container_width=True)

        # 3. Forecast Chart
        st.divider()
        st.subheader("📊 5-Day Temperature Forecast (3-Hour Intervals)")
        forecast_data = get_forecast(data['name'])
        
        if forecast_data:
            df_forecast = pd.DataFrame([
                {"Time": i["dt_txt"], "Temp (°C)": i["main"]["temp"], "Condition": i["weather"][0]["main"]}
                for i in forecast_data["list"]
            ])
            
            # Modern Area Chart
            fig = px.area(df_forecast, x="Time", y="Temp (°C)", 
                          hover_data=["Condition"],
                          color_discrete_sequence=['#4fc3f7'])
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="white",
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("❌ City not found. Please check the spelling or try a nearby major city.")
