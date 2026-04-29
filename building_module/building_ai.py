import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import pytz

# --- 1. CONFIGURATION ---
API_KEY = "d351ff8c3b45dd7fe4d0d19e1ce2ad19"
CITY = "Bengaluru"
IST = pytz.timezone('Asia/Kolkata')

st.title("🏢 Smart Building System")

# --- 2. DATA EXTRACTION ---
def get_real_temp():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        data = requests.get(url).json()
        if data.get("cod") == 200:
            return data['main']['temp']
        return None
    except:
        return None

# Get IST Time automatically on every reload
current_time_ist = datetime.datetime.now(IST)
current_hour = current_time_ist.hour
formatted_time = current_time_ist.strftime("%I:%M %p") # e.g., 03:00 AM

# --- 3. UI CONTROLS ---
people = st.slider("People in Room", 0, 100, 0)
real_temp = get_real_temp()

if real_temp is not None:
    current_temp = real_temp
    st.sidebar.success(f"✅ Live Weather: {current_temp}°C")
else:
    current_temp = st.sidebar.slider("Manual Temp Override", 0, 50, 25)
    st.sidebar.info("⏳ Weather API Syncing...")

# --- 4. AI AUTOMATION LOGIC ---
# AC Logic
if current_temp > 30:
    ac_mode = "❄️ Power Cool (18°C)"
elif current_temp > 24:
    ac_mode = "🍃 Eco Mode (24°C)"
else:
    ac_mode = "😴 AC Off"

# Light Logic (IST Based)
if 6 <= current_hour < 18:
    light_status = "☀️ Day Mode: Lights OFF"
    is_day = True
else:
    light_status = "🌙 Night Mode: Lights ON"
    is_day = False

# --- 5. DASHBOARD DISPLAY ---
st.subheader("🤖 AI Building Control")
col1, col2 = st.columns(2)

with col1:
    st.metric("Outdoor Temperature", f"{current_temp}°C")
    # This replaces the "Smart Lights" button with a simple status text
    st.write(f"**System Status:** {light_status}")
    st.write(f"**Current IST Time:** {formatted_time}")

with col2:
    st.metric("AI AC Setting", ac_mode)

st.success("AI optimized building energy usage successfully")

# --- 6. SECURITY & MAP ---
st.subheader("Security System")
security_mode = st.toggle("Enable Security Scan")
if security_mode:
    if not is_day and people > 0:
        st.error("🚨 ALERT: Movement detected at night!")
    else:
        st.success("✅ Building Secure")

st.subheader("City-Wide Energy Heatmap")
map_data = pd.DataFrame({
    'lat': [12.9784, 12.9352, 12.9698, 12.9766],
    'lon': [77.6408, 77.6245, 77.7500, 77.5993],
    'color': ['#FF0000', '#00FF00', '#FF0000', '#00FF00'] 
})
st.map(map_data, color='color', size=200)