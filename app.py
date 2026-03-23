import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
from streamlit_js_eval import get_geolocation

# ================= CONFIG =================
API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"
st.set_page_config(page_title="Weather Pro Ultimate", layout="wide", page_icon="🌤")

# ================= SESSION STATE =================
if "city_name" not in st.session_state:
    st.session_state.city_name = "Suryapet"

# ================= FUNCTIONS =================
def get_city_name(lat, lon):
    try:
        url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
        res = requests.get(url).json()
        return res[0]['name'] if res else None
    except:
        return None

def fetch_all_weather(city):
    try:
        curr = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric").json()
        if curr.get("cod") != 200: return None
        fore = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric").json()
        return {"current": curr, "forecast": fore}
    except:
        return None

# ================= UI =================
st.title("🌡️ Weather Pro Ultimate")

col1, col2 = st.columns([4,1])

with col1:
    # Manual search
    user_input = st.text_input("Search City", value=st.session_state.city_name)
    if user_input != st.session_state.city_name:
        st.session_state.city_name = user_input
        st.rerun()

with col2:
    st.write("##")
    if st.button("📍 Auto-Detect"):
        # This triggers the browser popup
        loc = get_geolocation()
        if loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            new_city = get_city_name(lat, lon)
            if new_city:
                st.session_state.city_name = new_city
                st.rerun()
        else:
            st.info("Waiting for GPS... (Make sure to click 'Allow' in your browser)")

# ================= RESULTS =================
data = fetch_all_weather(st.session_state.city_name)

if data:
    w = data['current']
    f = data['forecast']
    
    # Hero Card
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 20px; border-left: 10px solid #FFD700;">
        <h3 style="margin:0; opacity:0.8;">Currently in</h3>
        <h1 style="margin:0; font-size: 3rem;">{w['name']}</h1>
        <h2 style="font-size: 4rem; margin:10px 0;">{round(w['main']['temp'])}°C</h2>
        <p style="font-size: 1.5rem; text-transform: capitalize;">{w['weather'][0]['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Humidity", f"{w['main']['humidity']}%")
    m2.metric("Wind", f"{w['wind']['speed']} m/s")
    m3.metric("Feels Like", f"{round(w['main']['feels_like'])}°C")

    # Forecast
    st.divider()
    st.subheader("📊 5-Day Trend")
    df_f = pd.DataFrame([{"Time": i["dt_txt"], "Temp": i["main"]["temp"]} for i in f["list"]])
    fig = px.area(df_f, x="Time", y="Temp", template="plotly_dark", color_discrete_sequence=['#FFD700'])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"Could not find weather for '{st.session_state.city_name}'. Check spelling!")
