import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geocoder
from difflib import get_close_matches


API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

st.set_page_config(page_title="Weather Pro", layout="wide")

# ================= BACKGROUND =================
st.markdown("""
<style>

/* ================= BACKGROUND ================= */
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1c92d2);
    background-size: 400% 400%;
    animation: gradient 12s ease infinite;
    color: white;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* ================= CARD ================= */
.card {
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(12px);
}

/* ===== REALISTIC CLOUD ===== */
/* ===== ULTRA REALISTIC CLOUD ===== */
.cloud {
    position: fixed;
    width: 220px;
    height: 80px;

    /* soft cloud using gradients */
    background:
        radial-gradient(circle at 30% 50%, rgba(255,255,255,0.9) 40%, transparent 60%),
        radial-gradient(circle at 60% 40%, rgba(255,255,255,0.85) 35%, transparent 60%),
        radial-gradient(circle at 80% 60%, rgba(255,255,255,0.8) 30%, transparent 60%),
        radial-gradient(circle at 50% 70%, rgba(255,255,255,0.75) 35%, transparent 65%);

    filter: blur(1.5px); /* softness */
    border-radius: 100px;

    animation: cloudMove linear infinite;
    z-index: 0;
}

/* smooth infinite movement */
@keyframes cloudMove {
    0% { transform: translateX(-30vw); }
    100% { transform: translateX(120vw); }
}

/* depth layers */
.cloud.slow {
    animation-duration: 90s;
    opacity: 0.35;
}

.cloud.medium {
    animation-duration: 55s;
    opacity: 0.6;
}

.cloud.fast {
    animation-duration: 30s;
    opacity: 0.9;
}


/* ===== SMOOTH CONTINUOUS MOVEMENT ===== */
@keyframes cloudMove {
    0% { transform: translateX(-20vw); }
    100% { transform: translateX(120vw); }
}

/* depth layers */
.cloud.slow { animation-duration: 80s; opacity: 0.4; }
.cloud.medium { animation-duration: 50s; opacity: 0.6; }
.cloud.fast { animation-duration: 30s; opacity: 0.9; }



/* ================= SUN ================= */
.sun {
    position: fixed;
    top: 80px;
    right: 100px;
    width: 90px;
    height: 90px;
    background: radial-gradient(circle, #FFD700, #FF8C00);
    border-radius: 50%;
    animation: sunMove 8s ease-in-out infinite;
    box-shadow: 0 0 50px rgba(255,200,0,0.6);
}

@keyframes sunMove {
    0% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
    100% { transform: translateY(0); }
}

/* keep UI above animation */
.block-container {
    position: relative;
    z-index: 1;
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

                # Fix wrong detections
                if city in ["hyderabad", "the dalles", ""]:
                    return "suryapet"

                return city

        return "suryapet"

    except:
        return "suryapet"

# ================= SESSION INIT =================
if "city" not in st.session_state:
    st.session_state["city"] = detect_location()

if "auto_detect" not in st.session_state:
    st.session_state["auto_detect"] = False

# ================= HANDLE AUTO DETECT (BEFORE INPUT) =================
if st.session_state["auto_detect"]:
    st.session_state["city"] = detect_location()
    st.session_state["auto_detect"] = False

# ================= INPUT =================
col1, col2 = st.columns([3,1])

with col1:
    st.text_input("Enter City", key="city")

with col2:
    st.write("")
    if st.button("📍 Auto Detect"):
        st.session_state["auto_detect"] = True
        st.rerun()

# always use this
city = st.session_state["city"].lower()
# ================= ALIASES =================
# ================= SMART CITY SYSTEM =================
city_alias = {
    # Telangana
    "ranga reddy": "hyderabad",
    "rangareddy": "hyderabad",
    "medchal": "hyderabad",
    "sangareddy": "hyderabad",
    "karimnagar": "karimnagar",
    "warangal": "warangal",
    "suryapet": "suryapet",

    # Andhra
    "east godavari": "rajahmundry",
    "west godavari": "eluru",
    "krishna": "vijayawada",
    "prakasam": "ongole",

    # India common
    "vizag": "visakhapatnam",
    "vishakapatnam": "visakhapatnam",
    "hyd": "hyderabad",
    "secunderabad": "hyderabad",
    "bangalore": "bengaluru",
    "bombay": "mumbai",
    "madras": "chennai",
    "calcutta": "kolkata",
    "delhi": "new delhi"
}

# STEP 1: Direct match
if city in city_alias:
    city = city_alias[city]

# STEP 2: Fuzzy match (handles typos)
else:
    match = get_close_matches(city, city_alias.keys(), n=1, cutoff=0.7)
    if match:
        city = city_alias[match[0]]

# ================= WEATHER =================
if st.button("Get Weather"):
    if city:
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

            # ================= ANIMATION =================
            # Clouds (always)
            # ================= REALISTIC CLOUD SYSTEM =================

            # BACK LAYER (slow clouds)
            st.markdown('<div class="cloud slow" style="top:80px; left:10%;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="cloud slow" style="top:200px; left:60%;"></div>', unsafe_allow_html=True)
            
            # MID LAYER
            st.markdown('<div class="cloud medium" style="top:140px; left:30%;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="cloud medium" style="top:260px; left:80%;"></div>', unsafe_allow_html=True)
            
            # FRONT LAYER (fast clouds)
            st.markdown('<div class="cloud fast" style="top:100px; left:50%;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="cloud fast" style="top:220px; left:0%;"></div>', unsafe_allow_html=True)
                            
                        
            # Sun only if clear
            if "clear" in weather:
                st.markdown('<div class="sun"></div>', unsafe_allow_html=True)

            # ================= ICON =================
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

            # ================= DISPLAY =================
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.success(f"📍 {city.title()}")

                st.markdown(f"# {icon} {temp}°C")

                st.metric("Feels Like", f"{feels} °C")
                st.metric("Humidity", f"{humidity}%")
                st.metric("Wind Speed", f"{wind} m/s")

                st.write(f"Condition: {weather.title()}")
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
