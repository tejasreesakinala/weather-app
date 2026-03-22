import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
import time

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="Weather Pro", layout="wide")

# ================= UI STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1c92d2);
    background-size: 400% 400%;
    animation: gradient 10s ease infinite;
    color: white;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.card {
    background: rgba(255,255,255,0.1);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.title("🌤 Weather Pro Dashboard")

# ================= LOCATION DETECT =================
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            lat, lon = g.latlng
            url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
            data = requests.get(url).json()

            if data:
                city = data[0]["name"].lower()

                if city in ["hyderabad", "the dalles", ""]:
                    return "suryapet"

                return city

        return "suryapet"
    except:
        return "suryapet"

# ================= SEARCH API =================
def search_city(query):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={API_KEY}"
    res = requests.get(url).json()

    results = []
    for place in res:
        results.append(f"{place['name']}, {place['country']}")
    return results

# ================= SESSION =================
if "city" not in st.session_state:
    st.session_state["city"] = detect_location()

# ================= SEARCH =================
col1, col2 = st.columns([3,1])

with col1:
    search = st.text_input("🔍 Search City", value=st.session_state["city"])

    city = ""

    if search:
        suggestions = search_city(search)

        if suggestions:
            if len(suggestions) == 1:
                city = suggestions[0].split(",")[0].lower()
                st.success(f"Auto selected: {suggestions[0]}")
            else:
                st.caption("💡 Select correct city")
                selected = st.selectbox("Suggestions", suggestions)
                city = selected.split(",")[0].lower()
        else:
            city = search.lower()

with col2:
    st.write("")
    if st.button("📍 Auto Detect"):
        st.session_state["city"] = detect_location()
        st.rerun()

# fallback
if city:
    st.session_state["city"] = city

city = st.session_state["city"]

# ================= WEATHER =================
if st.button("Get Weather"):

    with st.spinner("Fetching weather... 🌦"):
        time.sleep(1)

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()

        if str(data.get("cod")) != "200":
            st.error("❌ City not found")
        else:
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            weather = data["weather"][0]["description"]

            lat = data["coord"]["lat"]
            lon = data["coord"]["lon"]

            # ICON
            if "clear" in weather:
                icon = "☀️"
            elif "cloud" in weather:
                icon = "☁️"
            elif "rain" in weather:
                icon = "🌧"
            elif "storm" in weather:
                icon = "⛈"
            else:
                icon = "🌤"

            # ================= CARD =================
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.success(f"📍 {city.title()}")

            col1, col2 = st.columns([1,1])

            with col1:
                st.markdown(f"# {icon} {temp}°C")
                st.metric("Feels Like", f"{feels} °C")
                st.metric("Humidity", f"{humidity}%")
                st.metric("Wind Speed", f"{wind} m/s")
                st.write(f"Condition: {weather.title()}")

            with col2:
                df = pd.DataFrame({"lat":[lat], "lon":[lon]})
                st.map(df)

            st.markdown('</div>', unsafe_allow_html=True)

            # ================= FORECAST =================
            st.subheader("📊 5-Day Forecast")

            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
            forecast = requests.get(forecast_url).json()

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
