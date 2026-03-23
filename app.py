import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
from streamlit_js_eval import get_geolocation


# Fix wrong server locations (Streamlit Cloud issue)
INVALID_LOCATIONS = ["the dalles", "boardman", "oregon"]

def fix_city(city):
    if city :
        city_lower = city.lower()
        for invalid in INVALID_LOCATIONS :
            if invalid in city_lower:
                return "Hyderabad"
    return city
    
if "city_name" not in st.session_state:
    st.session_state.city_name = "Suryapet"

# ================= CONFIG =================
API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"
st.set_page_config(page_title="Weather Pro Ultimate", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1c92d2);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    color: white;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.main-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
    border-radius: 30px;
    padding: 40px;
    text-align: center;
}

.block-container {
    position: relative;
    z-index: 10;
}

/* animations */
@keyframes cloudMove {
    from { transform: translateX(-120vw); }
    to { transform: translateX(120vw); }
}

@keyframes rainFall {
    from { transform: translateY(-100px); }
    to { transform: translateY(110vh); }
}
</style>
""", unsafe_allow_html=True)

# ================= CLOUDS (ALWAYS RUN) =================
cloud_html = ""
for _ in range(10):
    cloud_html += f"""
    <div style="
        position: fixed;
        top:{random.randint(50,400)}px;
        width:{random.randint(120,220)}px;
        height:60px;
        background:
            radial-gradient(circle at 30% 50%, white 40%, transparent 70%),
            radial-gradient(circle at 60% 40%, white 35%, transparent 70%),
            radial-gradient(circle at 80% 60%, white 30%, transparent 70%);
        filter: blur(15px);
        opacity:{random.uniform(0.2,0.5)};
        animation: cloudMove {random.randint(60,120)}s linear {random.randint(-120,0)}s infinite;
        border-radius:50px;
        z-index:0;
    "></div>
    """
st.markdown(cloud_html, unsafe_allow_html=True)

# ================= FUNCTIONS =================
def get_city_name(lat, lon):
    try:
        url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
        res = requests.get(url, timeout=5).json()
        return res[0]['name'] if res else None
    except:
        return None


def fetch_data(city):
    try:
        curr = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric",
            timeout=5
        ).json()

        if curr.get("cod") != 200:
            return None

        fore = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric",
            timeout=5
        ).json()

        if fore.get("cod") != "200":
            return None

        return {"current": curr, "forecast": fore}

    except:
        return None

# ================= TITLE =================
st.title("🌤 Weather Pro Ultimate")


st.caption("📍 Location: " + st.session_state.city_name)
st.write("Current City:", st.session_state.city_name)

# ================= INPUT =================
col_search, col_gps = st.columns([4,1])


# ===== SEARCH =====
with col_search:
    city = st.text_input(
        "Search City",
        key="city_name"   # ✅ SAME KEY as session_state
    )

def get_ip_location():
    try:
        # Primary API
        res = requests.get("https://ipinfo.io/json", timeout=5).json()
        city = res.get("city")
        if city:
            return city
        # Backup API
        res2 = requests.get("https://ipapi.co/json/", timeout=5).json()
        return res2.get("city")

    except:
        return None



# ===== AUTO DETECT =====
# ===== AUTO DETECT FUNCTION =====
def auto_detect_city():
    detected_city = get_ip_location()
    detected_city = fix_city(detected_city)

    # if detection is too generic → use your default
    if not detected_city or detected_city.lower() in ["hyderabad"]:
        detected_city = "Suryapet"

    st.session_state.city_name = detected_city


# ===== AUTO DETECT BUTTON =====
with col_gps:
    st.write("")
    st.button("📍 Auto Detect", on_click=auto_detect_city)
# ===== FETCH (OUTSIDE COLUMNS) =====
data = fetch_data(st.session_state.city_name)

       
       
# ================= EFFECTS =================
if data:
    w = data["current"]
    condition = w["weather"][0]["main"].lower()
    hour = datetime.now().hour

    # SUN / MOON
    if "clear" in condition:
        if 6 <= hour < 18:
            st.markdown("""
            <div style="
                position: fixed;
                top:80px;
                right:80px;
                width:140px;
                height:140px;
                background: radial-gradient(circle, #FFD54F 0%, transparent 70%);
                filter: blur(10px);
                z-index:0;
            "></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                position: fixed;
                top:80px;
                right:80px;
                width:100px;
                height:100px;
                background: radial-gradient(circle, white 0%, transparent 70%);
                filter: blur(6px);
                z-index:0;
            "></div>
            """, unsafe_allow_html=True)

    # RAIN
    if "rain" in condition or "drizzle" in condition:
        rain_html = ""
        for _ in range(50):
            rain_html += f"""
            <div style="
                position: fixed;
                left:{random.randint(0,100)}%;
                width:2px;
                height:20px;
                background: rgba(255,255,255,0.4);
                animation: rainFall {random.uniform(0.5,1.2)}s linear infinite;
                z-index:0;
            "></div>
            """
        st.markdown(rain_html, unsafe_allow_html=True)

# ================= DISPLAY =================
if data:
    w = data["current"]
    f = data["forecast"]

    st.markdown(f"""
    <div class="main-card">
        <h2>{w['name']}</h2>
        <h1 style="font-size:60px;">{round(w['main']['temp'])}°C</h1>
        <p style="font-size:20px;">{w['weather'][0]['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Humidity", f"{w['main']['humidity']}%")
    m2.metric("Wind", f"{w['wind']['speed']} m/s")
    m3.metric("Feels", f"{round(w['main']['feels_like'])}°C")

    st.map(pd.DataFrame({
        "lat":[w['coord']['lat']],
        "lon":[w['coord']['lon']]
    }))

    # Forecast
    st.subheader("📊 Forecast")
    df = pd.DataFrame([
        {"Time": i["dt_txt"], "Temp": i["main"]["temp"]}
        for i in f["list"]
    ])

    fig = px.line(df, x="Time", y="Temp", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("❌ City not found")
