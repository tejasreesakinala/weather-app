import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
import time

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="WeatherX", layout="wide")

# ================= CACHE =================
@st.cache_data(ttl=300)
def get_weather_by_coords(city):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo = requests.get(geo_url).json()

        if not geo:
            return None

        lat = geo[0]["lat"]
        lon = geo[0]["lon"]

        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        weather = requests.get(weather_url).json()

        return weather

    except:
        return None


@st.cache_data(ttl=300)
def get_forecast_by_coords(city):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo = requests.get(geo_url).json()

    if not geo:
        return None

    lat = geo[0]["lat"]
    lon = geo[0]["lon"]

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
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
                city = data[0]["name"].lower()

                # fallback fix
                if city in ["hyderabad", "the dalles", ""]:
                    return "suryapet"

                return city
    except:
        pass

    return "suryapet"


# ================= SEARCH =================
def search_city(query):
    try:
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={API_KEY}"
        res = requests.get(url).json()
        return [f"{p['name']}, {p['country']}" for p in res]
    except:
        return []


# ================= SESSION =================
if "city" not in st.session_state:
    st.session_state.city = detect_location()

if "favorites" not in st.session_state:
    st.session_state.favorites = []


# ================= UI =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.title("🌤 WeatherX")

# ================= HEADER =================
col1, col2, col3 = st.columns([3,1,1])

with col1:
    search = st.text_input("🔍 Search City", value=st.session_state.city)

    city = ""

    if search:
        suggestions = search_city(search)

        if suggestions:
            if len(suggestions) == 1:
                city = suggestions[0].split(",")[0].lower()
            else:
                selected = st.selectbox("Suggestions", suggestions)
                city = selected.split(",")[0].lower()
        else:
            city = search.lower()

with col2:
    if st.button("📍 Detect"):
        st.session_state.city = detect_location()
        st.rerun()

with col3:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

if city:
    st.session_state.city = city

city = st.session_state.city

# ================= WEATHER =================
with st.spinner("Loading weather..."):
    time.sleep(0.5)
    data = get_weather_by_coords(city)

if not data or str(data.get("cod")) != "200":
    st.error("❌ Location not found")
else:
    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    weather = data["weather"][0]["description"]

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
            st.rerun()

    # ================= MAIN =================
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

    forecast = get_forecast_by_coords(city)

    if forecast and "list" in forecast:
        temps = []
        days = []

        for i in range(0, 40, 8):
            item = forecast["list"][i]
            temps.append(item["main"]["temp"])
            days.append(item["dt_txt"].split()[0])

        df_chart = pd.DataFrame({
            "Day": days,
            "Temperature": temps
        })

        fig = px.line(df_chart, x="Day", y="Temperature", markers=True)
        st.plotly_chart(fig, use_container_width=True)
