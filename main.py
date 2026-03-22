import tkinter as tk
import requests
import time
import geocoder
import webbrowser
import matplotlib.pyplot as plt
import random

API_KEY = "1a6b0e5216a955f75ea2e9a0a5a2edcc"

# ================= ROOT =================
root = tk.Tk()
root.title("Weather Pro Premium")
root.geometry("900x650")
root.configure(bg="#0f2027")

# ================= CANVAS =================
canvas = tk.Canvas(root, width=900, height=650, highlightthickness=0)
canvas.place(x=0, y=0)

# ================= SIDEBAR =================
sidebar = tk.Frame(root, bg="#111827", width=200)
sidebar.pack(side="left", fill="y")

tk.Label(sidebar, text="☁ Weather App", fg="white",
         bg="#111827", font=("Arial", 14, "bold")).pack(pady=20)

# ================= MAIN AREA =================
main_frame = tk.Frame(root, bg="#0f2027")
main_frame.pack(fill="both", expand=True)

# ================= HEADER =================
header = tk.Label(main_frame, text="Weather Dashboard",
                  font=("Arial", 22, "bold"),
                  fg="white", bg="#0f2027")
header.pack(pady=10)

time_label = tk.Label(main_frame, fg="white", bg="#0f2027")
time_label.pack()

def update_time():
    time_label.config(text=time.strftime("%d %b %Y | %H:%M:%S"))
    root.after(1000, update_time)

update_time()

# ================= GLASS CARD =================
card = tk.Frame(main_frame, bg="#1e293b", bd=0)
card.pack(pady=40, ipadx=20, ipady=20)

tk.Label(card, text="Search Weather",
         fg="white", bg="#1e293b").pack(pady=5)

city_entry = tk.Entry(card, font=("Arial", 14), justify="center")
city_entry.pack(pady=10)

# ================= OUTPUT =================
icon_label = tk.Label(card, font=("Arial", 40),
                      bg="#1e293b", fg="white")
icon_label.pack()

city_label = tk.Label(card, font=("Arial", 18, "bold"),
                      bg="#1e293b", fg="#38bdf8")
city_label.pack()

temp_label = tk.Label(card, font=("Arial", 36, "bold"),
                      bg="#1e293b", fg="white")
temp_label.pack()

weather_label = tk.Label(card, bg="#1e293b", fg="white")
weather_label.pack()

humidity_label = tk.Label(card, bg="#1e293b", fg="white")
humidity_label.pack()

map_label = tk.Label(card, fg="#22c55e", bg="#1e293b", cursor="hand2")
map_label.pack(pady=5)

# ================= ICON =================
def get_icon(w):
    w = w.lower()
    if "clear" in w: return "☀️"
    if "cloud" in w: return "☁️"
    if "rain" in w: return "🌧"
    if "storm" in w: return "⛈"
    return "🌤"

# ================= ANIMATIONS =================
clouds = []
rain = []

def clear_canvas():
    canvas.delete("all")
    clouds.clear()
    rain.clear()

def clouds_anim():
    for i in range(5):
        x = random.randint(200,800)
        y = random.randint(50,200)
        c = canvas.create_oval(x,y,x+100,y+50,fill="white",outline="")
        clouds.append(c)
    move_clouds()

def move_clouds():
    for c in clouds:
        canvas.move(c,2,0)
        x1,y1,x2,y2 = canvas.coords(c)
        if x1 > 900:
            canvas.coords(c,200,y1,300,y2)
    root.after(50, move_clouds)

def rain_anim():
    for i in range(80):
        x = random.randint(200,900)
        d = canvas.create_line(x,0,x,10,fill="#38bdf8")
        rain.append(d)
    move_rain()

def move_rain():
    for d in rain:
        canvas.move(d,0,10)
        x1,y1,x2,y2 = canvas.coords(d)
        if y1 > 650:
            canvas.coords(d,x1,0,x2,10)
    root.after(50, move_rain)

def sun_anim():
    canvas.create_oval(750,50,850,150,fill="yellow")

def lightning():
    def flash():
        canvas.create_rectangle(0,0,900,650,fill="white")
        root.after(100, clear_canvas)
        root.after(3000, flash)
    flash()

def night():
    canvas.create_rectangle(0,0,900,650,fill="#020617")
    for i in range(50):
        canvas.create_oval(random.randint(0,900),random.randint(0,650),
                           random.randint(0,900)+2,random.randint(0,650)+2,
                           fill="white")

# ================= LOCATION =================
def detect_location():
    try:
        g = geocoder.ip('me')
        if g.latlng:
            lat, lon = g.latlng
            url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=5&appid={API_KEY}"
            data = requests.get(url).json()

            if data:
                city = data[0]["name"].lower()
                if city == "hyderabad":
                    city = "Suryapet"

                city_entry.delete(0, tk.END)
                city_entry.insert(0, city.title())
    except:
        city_entry.insert(0,"Suryapet")

# ================= WEATHER =================
def get_weather():
    city = city_entry.get().strip()

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric"
        data = requests.get(url).json()

        if str(data.get("cod")) != "200":
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            data = requests.get(url).json()

        if str(data.get("cod")) != "200":
            city_label.config(text="❌ City not found")
            return

        temp = data["main"]["temp"]
        weather = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        icon_label.config(text=get_icon(weather))
        city_label.config(text=city.title())
        temp_label.config(text=f"{temp}°C")
        weather_label.config(text=weather.title())
        humidity_label.config(text=f"💧 {humidity}%")

        clear_canvas()

        if "clear" in weather:
            sun_anim()
        elif "cloud" in weather:
            clouds_anim()
        elif "rain" in weather:
            rain_anim()
        elif "storm" in weather:
            rain_anim()
            lightning()

        hour = int(time.strftime("%H"))
        if hour >= 18 or hour <= 6:
            night()

        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        if city.lower() == "suryapet":
            lat, lon = 17.1405,79.6200

        map_url = f"https://www.google.com/maps?q={lat},{lon}"
        map_label.config(text="🗺 Open Map")
        map_label.bind("<Button-1>", lambda e: webbrowser.open(map_url))

    except Exception as e:
        print(e)
        city_label.config(text="⚠️ Error")

# ================= FORECAST =================
def get_forecast():
    city = city_entry.get().strip()
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    temps, days = [], []

    for i in range(0,40,8):
        temps.append(data["list"][i]["main"]["temp"])
        days.append(data["list"][i]["dt_txt"].split()[0])

    plt.plot(days, temps, marker='o')
    plt.title("5-Day Forecast")
    plt.show()

# ================= BUTTONS =================
tk.Button(card, text="Get Weather", command=get_weather, bg="#38bdf8").pack(pady=5)
tk.Button(card, text="Auto Detect Location", command=detect_location, bg="#22c55e").pack(pady=5)
tk.Button(card, text="Forecast Graph", command=get_forecast, bg="#f59e0b").pack(pady=5)

root.mainloop()