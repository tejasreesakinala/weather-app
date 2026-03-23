import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
from streamlit_js_eval import get_geolocation

# ================= CONFIG =================
API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"
st.set_page_config(page_title="Weather Pro Ultimate", layout="wide")

# ================= SESSION STATE =================
if "city_name" not in st.session_state:
    st.session_state.city_name = "Suryapet"

# ================= ADVANCED STYLING =================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1c92d2);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .main-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 25px 45px rgba(0,0,0,0.2);
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .metric-container {
        background: rgba(0, 0, 0, 0.2);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================
def get_city_name(lat, lon):
    try:
        url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
        res = requests.get(url).json()
        return res[0]['name'] if res else None
    except: return None

def fetch_data(city):
    curr = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric").json()
    if curr.get("cod") != 200: return None
    fore = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric").json()
    return {"current": curr, "forecast": fore}

# ================= UI LAYOUT =================
st.title("🌡️ Weather Pro Ultimate")

# Search and Locate Row
col_search, col_gps = st.columns([4, 1])

with col_search:
    new_input = st.text_input("Search City", value=st.session_state.city_name, placeholder="Type a city name...")
    if new_input != st.session_state.city_name:
        st.session_state.city_name = new_input
        st.rerun()

with col_gps:
    st.write("##")
    if st.button("📍 Auto-Detect (GPS)"):
        location = get_geolocation()
        if location:
            lat = location['coords']['latitude']
            lon = location['coords']['longitude']
            detected = get_city_name(lat, lon)
            if detected:
                st.session_state.city_name = detected
                st.rerun()
        else:
            st.info("Please allow location access in your browser pop-up!")

# ================= DISPLAY DATA =================
data = fetch_data(st.session_state.city_name)

if data:
    w = data['current']
    f = data['forecast']
    
    # Hero Card
    st.markdown(f"""
    <div class="main-card">
        <p style="font-size: 1.2rem; opacity: 0.7; margin-bottom: 0;">Currently in</p>
        <h1 style="font-size: 4.5rem; font-weight: 800; margin: 0;">{w['name']}</h1>
        <h2 style="font-size: 5.5rem; color: #fccb90; margin: 10px 0;">{round(w['main']['temp'])}°C</h2>
        <p style="font-size: 1.8rem; text-transform: capitalize; letter-spacing: 2px;">{w['weather'][0]['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Detailed Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Feels Like", f"{round(w['main']['feels_like'])}°C")
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Humidity", f"{w['main']['humidity']}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Wind Speed", f"{w['wind']['speed']} m/s")
        st.markdown('</div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Pressure", f"{w['main']['pressure']} hPa")
        st.markdown('</div>', unsafe_allow_html=True)

    # Forecast Visual
    st.write("### 📅 5-Day Forecast Trend")
    df_f = pd.DataFrame([{"Time": i["dt_txt"], "Temp": i["main"]["temp"]} for i in f["list"]])
    
    fig = px.area(df_f, x="Time", y="Temp", 
                  template="plotly_dark", 
                  color_discrete_sequence=['#4facfe'])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("City not found. Please check your spelling.")
