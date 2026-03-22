import streamlit as st
import requests

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="Weather App")

st.title("🌤 Weather Dashboard")

city = st.text_input("Enter City")

if st.button("Get Weather"):
    if city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()

        if str(data.get("cod")) != "200":
            st.error("City not found")
        else:
            st.success(f"📍 {city.title()}")
            st.write(f"🌡 Temperature: {data['main']['temp']} °C")
            st.write(f"☁ Weather: {data['weather'][0]['description']}")
            st.write(f"💧 Humidity: {data['main']['humidity']}%")