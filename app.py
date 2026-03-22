import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="Weather Pro", layout="wide")

# 🌈 UI STYLE
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}
.card {
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)

st.title("🌤 Weather Pro Dashboard")

# ================= LOCATION DETECT =================
def detect_location():
    try:
        g = geocoder.ip('me')
        return g.city
    except:
        return ""

auto_city = detect_location()

# ================= INPUT =================
col1, col2 = st.columns([3,1])

with col1:
    city = st.text_input("Enter City", value=auto_city).lower()

with col2:
    st.write("")
    if st.button("📍 Auto Detect"):
        city = detect_location().lower()

# 🔥 aliases
aliases = {
    "vizag": "visakhapatnam",
    "hyd": "hyderabad",
    "delhi": "new delhi"
}
if city in aliases:
    city = aliases[city]

# ================= WEATHER =================
if st.button("Get Weather"):
    if city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()

        if str(data.get("cod")) != "200":
            st.error("City not found")
        else:
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            weather = data["weather"][0]["description"]

            sunrise = data["sys"]["sunrise"]
            sunset = data["sys"]["sunset"]

            # ================= DISPLAY =================
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.success(f"📍 {city.title()}")

                st.metric("🌡 Temperature", f"{temp} °C")
                st.metric("🤒 Feels Like", f"{feels} °C")
                st.metric("💧 Humidity", f"{humidity}%")
                st.metric("🌬 Wind", f"{wind} m/s")

                st.write(f"☁ {weather.title()}")
                st.markdown('</div>', unsafe_allow_html=True)

            # ================= MAP =================
            with col2:
                lat = data["coord"]["lat"]
                lon = data["coord"]["lon"]

                df = pd.DataFrame({"lat":[lat], "lon":[lon]})
                st.map(df)

            # ================= FORECAST =================
            st.subheader("📊 5-Day Forecast")

            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
            forecast_data = requests.get(forecast_url).json()

            temps = []
            days = []

            for i in range(0,40,8):
                item = forecast_data["list"][i]
                temps.append(item["main"]["temp"])
                days.append(item["dt_txt"].split()[0])

            df_chart = pd.DataFrame({
                "Day": days,
                "Temperature": temps
            })

            fig = px.line(df_chart, x="Day", y="Temperature", markers=True)
            st.plotly_chart(fig, use_container_width=True)
