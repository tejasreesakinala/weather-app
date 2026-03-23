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

# ================= SESSION STATE =================
if "city_input" not in st.session_state:
    st.session_state.city_input = "Suryapet"

# ================= SMART CITY SYSTEM =================
city_alias = {"vizag": "visakhapatnam", "hyd": "hyderabad", "bangalore": "bengaluru", "delhi": "new delhi"}

def normalize_city(city):
    city = city.lower().strip()
    return city_alias.get(city, city)

# ================= DATA FETCHING =================
@st.cache_data(ttl=600)
def get_weather_data(city):
    city = normalize_city(city)
    # Current Weather
    curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    curr_res = requests.get(curr_url).json()
    if curr_res.get("cod") != 200: return None
    
    # Air Pollution (using lat/lon from current weather)
    lat, lon = curr_res['coord']['lat'], curr_res['coord']['lon']
    poll_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    poll_res = requests.get(poll_url).json()
    
    # Forecast
    fore_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    fore_res = requests.get(fore_url).json()
    
    return {"current": curr_res, "pollution": poll_res, "forecast": fore_res}

# ================= CSS & DESIGN =================
def inject_ui(weather_main, hour):
    # Dynamic Gradient based on time
    if 6 <= hour < 17: bg = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
    elif 17 <= hour < 20: bg = "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
    else: bg = "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)"

    glow_color = "rgba(255, 255, 255, 0.3)"
    if "Rain" in weather_main: glow_color = "rgba(0, 191, 255, 0.5)"
    elif "Clear" in weather_main: glow_color = "rgba(255, 215, 0, 0.5)"

    st.markdown(f"""
    <style>
    .stApp {{ background: {bg}; color: white; transition: all 2s ease; }}
    .weather-card {{
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 30px;
        border: 1px solid {glow_color};
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }}
    .metric-box {{ text-align: center; padding: 10px; }}
    /* Visual Effects */
    .mist-overlay {{
        position: fixed; top:0; left:0; width:100vw; height:100vh;
        background: rgba(255,255,255,0.1); backdrop-filter: blur(5px);
        pointer-events: none; z-index: 1; display: {"block" if "Mist" in weather_main or "Haze" in weather_main else "none"};
    }}
    .rain {{ position: fixed; width: 2px; height: 20px; background: rgba(255,255,255,0.4); animation: fall linear infinite; pointer-events: none; z-index: 0; }}
    @keyframes fall {{ from {{ transform: translateY(-100px); }} to {{ transform: translateY(110vh); }} }}
    </style>
    <div class="mist-overlay"></div>
    """, unsafe_allow_html=True)

# ================= MAIN APP =================
inject_ui(st.session_state.get('w_main', 'Clear'), datetime.now().hour)

# Search Bar
col1, col2 = st.columns([4,1])
with col1:
    search_query = st.text_input("🌍 Explore a City...", value=st.session_state.city_input)
with col2:
    st.write("##")
    if st.button("📍 Locate"):
        g = geocoder.ip('me')
        if g.city: st.session_state.city_input = g.city; st.rerun()

# Processing
data = get_weather_data(search_query)

if data:
    w = data['current']
    p = data['pollution']
    f = data['forecast']
    st.session_state.w_main = w['weather'][0]['main']

    # Rain effect trigger
    if "Rain" in w['weather'][0]['main']:
        for _ in range(40):
            st.markdown(f'<div class="rain" style="left:{random.randint(0,100)}%; animation-duration:{random.uniform(0.5,1.5)}s; animation-delay:{random.uniform(0,2)}s;"></div>', unsafe_allow_html=True)

    # UI LAYOUT
    row1_1, row1_2 = st.columns([2, 1])

    with row1_1:
        st.markdown(f"""
        <div class="weather-card">
            <h4 style="margin:0; opacity:0.7;">{datetime.now().strftime('%A, %d %B')}</h4>
            <h1 style="font-size: 4rem; margin:0;">{w['name']}</h1>
            <div style="display:flex; align-items:center;">
                <h1 style="font-size: 5rem; color:#FFD700; margin-right:20px;">{round(w['main']['temp'])}°C</h1>
                <p style="font-size:1.5rem; text-transform:capitalize;">{w['weather'][0]['description']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Extended Metrics
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Feels Like", f"{round(w['main']['feels_like'])}°")
        m_col2.metric("Humidity", f"{w['main']['humidity']}%")
        m_col3.metric("Wind", f"{w['wind']['speed']} m/s")
        
        # AQI Logic
        aqi_val = p['list'][0]['main']['aqi']
        aqi_labels = {1:"Good", 2:"Fair", 3:"Moderate", 4:"Poor", 5:"Very Poor"}
        m_col4.metric("Air Quality", aqi_labels.get(aqi_val, "N/A"))

    with row1_2:
        st.write("### 🗺️ Context Map")
        st.map(pd.DataFrame({"lat": [w['coord']['lat']], "lon": [w['coord']['lon']]}), zoom=10)

    # Forecast Section
    st.markdown("### 📊 5-Day Temperature Trend")
    df_f = pd.DataFrame([{"Time": i["dt_txt"], "Temp": i["main"]["temp"], "Condition": i["weather"][0]["main"]} for i in f["list"]])
    
    fig = px.area(df_f, x="Time", y="Temp", hover_data=["Condition"],
                  color_discrete_sequence=['rgba(255,255,255,0.4)'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                      font_color="white", xaxis_showgrid=False, yaxis_showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Could not find data for that city. Try checking your spelling!")
