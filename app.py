import streamlit as st
import requests

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="Weather App", layout="centered")

# 🌈 Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
    }
    .box {
        padding: 20px;
        border-radius: 15px;
        background-color: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌤 Weather Dashboard")

city = st.text_input("Enter City").lower()

# 🔥 Aliases
aliases = {
    "vizag": "visakhapatnam",
    "hyd": "hyderabad",
    "bengaluru": "bangalore",
    "delhi": "new delhi"
}

if city in aliases:
    city = aliases[city]

if st.button("Get Weather"):
    if city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()

        if str(data.get("cod")) != "200":
            st.error("City not found")
        else:
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]

            st.markdown('<div class="box">', unsafe_allow_html=True)

            st.success(f"📍 {city.title()}")
            st.metric("🌡 Temperature", f"{temp} °C")
            st.write(f"☁ Weather: {weather.title()}")
            st.write(f"💧 Humidity: {humidity}%")

            st.markdown('</div>', unsafe_allow_html=True)
