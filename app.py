import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
from datetime import datetime

API_KEY = "YOUR_API_KEY"

st.set_page_config(page_title="WeatherX", layout="wide")

# ================= CACHE =================
@st.cache_data(ttl=300)
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

@st.cache_data(ttl=300)
def get_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

# ================= LOCATION =================
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            lat, lon = g.latlng
            url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
            data = requests.get(url).json()
            if data:
                return data[0]["name"].lower()
    except:
        pass
    return "suryapet"

# ================= SESSION =================
if "city" not in st.session_state:
    st.session_state.city = detect_location()

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ================= THEME (DAY/NIGHT) =================
hour = datetime.now().hour
if hour >= 18 or hour <= 6:
    bg = "#0f2027"
else:
    bg = "#1c92d2"

# ================= UI =================
st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(135deg, {bg}, #203a43);
    color: white;
}}

.card {{
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}}
</style>
""", unsafe_allow_html=True)

st.title("🌤 WeatherX")

# ================= HEADER =================
col1, col2, col3 = st.columns([3,1,1])

with col1:
    city_input = st.text_input("🔍 Search city", value=st.session_state.city)

    if city_input:
        st.session_state.city = city_input.lower()

with col2:
    if st.button("📍 Detect"):
        st.session_state.city = detect_location()
        st.rerun()

with col3:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

city = st.session_state.city

# ================= WEATHER =================
data = get_weather(city)

if str(data.get("cod")) != "200":
    st.error("City not found")
else:
    temp = data["main"]["temp"]
    weather = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    feels = data["main"]["feels_like"]

    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]

    # ================= FAVORITES =================
    col1, col2 = st.columns([3,1])

    with col1:
        if st.button("⭐ Add to Favorites"):
            if city not in st.session_state.favorites:
                st.session_state.favorites.append(city)

    with col2:
        if st.session_state.favorites:
            selected = st.selectbox("⭐ Favorites", st.session_state.favorites)
            st.session_state.city = selected

    # ================= MAIN =================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])

    with col1:
        st.success(f"📍 {city.title()}")
        st.markdown(f"# {temp}°C")
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

    temps = []
    days = []

    for i in range(0,40,8):
        item = forecast["list"][i]
        temps.append(item["main"]["temp"])
        days.append(item["dt_txt"].split()[0])

    df_chart = pd.DataFrame({"Day": days, "Temp": temps})

    fig = px.line(df_chart, x="Day", y="Temp", markers=True)
    st.plotly_chart(fig, use_container_width=True)
