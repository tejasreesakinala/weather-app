import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
from streamlit_js_eval import get_geolocation # Accurate browser location

# ================= CONFIG =================
API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"
st.set_page_config(page_title="Weather Pro Ultimate", layout="wide", page_icon="🌤")

# ================= SESSION STATE =================
if "city_input" not in st.session_state:
    st.session_state.city_input = "Suryapet"

# ================= REVERSE GEOCoding =================
def get_city_from_coords(lat, lon):
    try:
        # Using OpenWeather's Reverse Geocoding API
        url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
        res = requests.get(url).json()
        if res:
            return res[0]['name']
    except:
        return None
    return None

def get_weather_data(city):
    curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    curr_res = requests.get(curr_url).json()
    if curr_res.get("cod") != 200: return None
    
    fore_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    fore_res = requests.get(fore_url).json()
    return {"current": curr_res, "forecast": fore_res}

# ================= MAIN APP =================
st.title("🌤 Weather Pro Ultimate")

col1, col2 = st.columns([4,1])

with col1:
    # Key 'city_input' maps directly to session_state
    query = st.text_input("Search City", key="city_input")

with col2:
    st.write("##")
    # THE FIX: Trigger browser geolocation
    if st.button("📍 Accurate Locate"):
        loc = get_geolocation()
        if loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            detected_city = get_city_from_coords(lat, lon)
            if detected_city:
                st.session_state.city_input = detected_city
                st.rerun()
        else:
            st.warning("Please allow location access in your browser.")

# ================= DISPLAY =================
data = get_weather_data(st.session_state.city_input)

if data:
    w = data['current']
    f = data['forecast']
    
    # Display Card
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 20px;">
        <h1 style="margin:0;">{w['name']}</h1>
        <h2 style="font-size: 4rem; color: #FFD700;">{round(w['main']['temp'])}°C</h2>
        <p style="font-size: 1.2rem;">{w['weather'][0]['description'].title()}</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    m1, m2, m3 = st.columns(3)
    m1.metric("Humidity", f"{w['main']['humidity']}%")
    m2.metric("Wind", f"{w['wind']['speed']} m/s")
    m3.metric("Feels Like", f"{round(w['main']['feels_like'])}°C")

    # Map & Forecast
    st.map(pd.DataFrame({"lat": [w['coord']['lat']], "lon": [w['coord']['lon']]}))
    
    st.subheader("📊 Temperature Trend")
    df_f = pd.DataFrame([{"Time": i["dt_txt"], "Temp": i["main"]["temp"]} for i in f["list"]])
    st.plotly_chart(px.line(df_f, x="Time", y="Temp", template="plotly_dark"), use_container_width=True)
else:
    st.error("City not found. Try searching for 'Suryapet' manually.")
