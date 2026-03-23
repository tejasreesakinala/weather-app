import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
from datetime import datetime
import random

# ================= CONFIG & CONSTANTS =================
API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"
st.set_page_config(page_title="Weather Pro Advanced", layout="wide", page_icon="🌤")

# ================= SESSION STATE INIT =================
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
if "city_input" not in st.session_state:
    st.session_state.city_input = "London" # Default starting city

# ================= ADVANCED UI STYLE =================
st.markdown("""
<style>
    /* Prevent horizontal scroll and set background */
    .main { overflow-x: hidden; }
    
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
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }

    /* Animations */
    .rain {
        position: fixed;
        width: 2px;
        height: 15px;
        background: rgba(255,255,255,0.4);
        top: -10%;
        z-index: 0;
        pointer-events: none;
        animation: fall linear infinite;
    }
    @keyframes fall { to { transform: translateY(110vh); } }

    .sun-glow {
        position: fixed;
        top: 50px;
        right: 50px;
        width: 120px;
        height: 120px;
        background: radial-gradient(circle, #ffca28 0%, rgba(255,202,40,0) 70%);
        filter: blur(20px);
        animation: pulse 4s ease-in-out infinite;
        z-index: 0;
    }
    @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

    /* Cloud styling */
    .cloud-svg {
        position: fixed;
        opacity: 0.3;
        z-index: 0;
        pointer-events: none;
        animation: float linear infinite;
    }
    @keyframes float {
        from { left: -20%; }
        to { left: 110%; }
    }
</style>
""", unsafe_allow_html=True)

# ================= HELPER FUNCTIONS =================
def get_weather(city_name):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return res
        return None
    except:
        return None

def get_forecast(city_name):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

# ================= DYNAMIC VISUAL EFFECTS =================
def render_effects(condition):
    condition = condition.lower()
    if "rain" in condition or "drizzle" in condition:
        for _ in range(50):
            left = random.randint(0, 100)
            dur = random.uniform(0.5, 1.5)
            delay = random.uniform(0, 2)
            st.markdown(f'<div class="rain" style="left:{left}%; animation-duration:{dur}s; animation-delay:{delay}s;"></div>', unsafe_allow_html=True)
    
    if "clear" in condition:
        st.markdown('<div class="sun-glow"></div>', unsafe_allow_html=True)

    # Ambient Clouds
    for i in range(5):
        top = random.randint(5, 40)
        dur = random.randint(60, 120)
        st.markdown(f'<div class="cloud-svg" style="top:{top}%; animation-duration:{dur}s;">☁️</div>', unsafe_allow_html=True)

# ================= MAIN UI =================
st.title("🌡️ Weather Pro Advanced")

# Search Bar Logic
col_search, col_gps = st.columns([4, 1])
with col_search:
    city_input = st.text_input("Enter City Name", value=st.session_state.city_input)
with col_gps:
    st.write("##")
    if st.button("📍 Locate"):
        g = geocoder.ip('me')
        if g.city:
            st.session_state.city_input = g.city
            st.rerun()

# Trigger Weather Fetch
if city_input:
    data = get_weather(city_input)
    if data:
        st.session_state.weather_data = data
        render_effects(data['weather'][0]['main'])
    else:
        st.error("City not found. Please try again.")

# Display Dashboard
if st.session_state.weather_data:
    w = st.session_state.weather_data
    
    # Hero Section
    col_main, col_map = st.columns([2, 2])
    
    with col_main:
        st.markdown(f"""
        <div class="weather-card">
            <h2 style='margin:0;'>{w['name']}, {w['sys']['country']}</h2>
            <p style='font-size: 1.2rem; opacity: 0.8;'>{datetime.now().strftime('%A, %b %d')}</p>
            <h1 style='font-size: 4rem; margin: 10px 0;'>{round(w['main']['temp'])}°C</h1>
            <p style='text-transform: capitalize; font-size: 1.5rem;'>{w['weather'][0]['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Humidity", f"{w['main']['humidity']}%")
        m2.metric("Wind", f"{w['wind']['speed']} m/s")
        m3.metric("Feels Like", f"{round(w['main']['feels_like'])}°C")

    with col_map:
        # Simple Map View
        map_data = pd.DataFrame({'lat': [w['coord']['lat']], 'lon': [w['coord']['lon']]})
        st.map(map_data, zoom=10, use_container_width=True)

    # Forecast Section
    st.divider()
    st.subheader("📅 5-Day Temperature Trend")
    forecast_data = get_forecast(w['name'])
    
    if forecast_data.get("cod") == "200":
        # Extract noon readings for a cleaner 5-day chart
        list_data = forecast_data['list']
        chart_df = pd.DataFrame([
            {
                "Time": item['dt_txt'],
                "Temp (°C)": item['main']['temp'],
                "Condition": item['weather'][0]['main']
            } for item in list_data
        ])
        
        fig = px.area(chart_df, x="Time", y="Temp (°C)", 
                      color_discrete_sequence=['#1c92d2'],
                      template="plotly_dark")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
