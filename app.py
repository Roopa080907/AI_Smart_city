import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import pytz
import folium
from streamlit_folium import st_folium
import joblib
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="AI Smart City Hub")

# --- 2. GLOBAL CONFIGURATION (Moved up for header logic) ---
IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.datetime.now(IST)
is_dark_now = now_ist.hour >= 18 or now_ist.hour < 6
light_display = "Night" if is_dark_now else "Day"

# --- AI CONTROL CENTER HEADER (ALWAYS VISIBLE) ---
st.title("⚡ SMART CITY AI CONTROL SYSTEM")
st.write("Real-time AI optimization of traffic, energy & lighting")

h1, h2, h3 = st.columns(3)
h1.metric("Traffic Load", "110")
h2.metric("Energy Usage", "40%")
h3.metric("Lighting", light_display)

# Using session state to manage activation/deactivation
if 'ai_active' not in st.session_state:
    st.session_state.ai_active = False

# Toggle logic for Activation/Deactivation
button_label = "🛑 Deactivate AI Smart City" if st.session_state.ai_active else "🚀 Activate AI Smart City"
if st.button(button_label):
    st.session_state.ai_active = not st.session_state.ai_active
    st.rerun()

# --- HIDDEN LOGIC: ONLY SHOWS IF AI IS ACTIVATED ---
if st.session_state.ai_active:
    st.success("AI Smart City Optimization Active!")
    st.markdown("---")

    # --- REST OF GLOBAL CONFIGURATION ---
    API_KEY = "d351ff8c3b45dd7fe4d0d19e1ce2ad19"
    CITY = "Bengaluru"

    # Load Streetlight Model logic
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "model.pkl")
    try:
        model = joblib.load(model_path)
        model_loaded = True
    except:
        model_loaded = False

    # --- 3. TABS NAVIGATION ---
    tab1, tab2, tab3 = st.tabs(["🚦 Traffic System", "🏢 Smart Building", "💡 AI Streetlights"])

    # ==========================================
    # 🚦 TAB 1: TRAFFIC SYSTEM (UPDATED)
    # ==========================================
    with tab1:
        st.title("🌍 AI Smart City - Intelligent Traffic System")
        tr_hour = st.sidebar.slider("Select Time (24h)", 0, 23, 18, key="tr_hour")
        tr_names = ["Majestic", "Indiranagar", "Silk Board", "Jayanagar"]
        tr_manual = [st.sidebar.slider(f"{name} Base Traffic", 0, 100, 40, key=f"tr_base_{name}") for name in tr_names]
        ambulance_mode = st.sidebar.checkbox("🚑 Emergency Mode", key="tr_amb")
        accident_mode = st.sidebar.checkbox("💥 Accident Mode", key="tr_acc")

        tr_junctions = [[12.9763, 77.5713], [12.9719, 77.6412], [12.9352, 77.6245], [12.9279, 77.5834]]

        def get_traffic_logic(h, base):
            t_list = base.copy()
            if 8 <= h <= 10: t_list = [t + inc for t, inc in zip(t_list, [20, 15, 30, 10])]
            elif 17 <= h <= 20: t_list = [t + inc for t, inc in zip(t_list, [25, 20, 35, 15])]
            return [min(100, t) for t in t_list]

        current_tr_data = get_traffic_logic(tr_hour, tr_manual)
        def get_green_time(t): return int(20 + (t / 100) * 40)
        def get_road_color(t): return "red" if t > 70 else "orange" if t > 40 else "green"

        m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, tiles="cartodb dark_matter")
        roads = [(tr_junctions[0], tr_junctions[1]), (tr_junctions[1], tr_junctions[2]), (tr_junctions[2], tr_junctions[3]), (tr_junctions[3], tr_junctions[0])]

        for i, r in enumerate(roads):
            avg_t = (current_tr_data[i] + current_tr_data[(i+1) % 4]) / 2
            folium.PolyLine(r, color=get_road_color(avg_t), weight=6, opacity=0.8).add_to(m)

        for i, coord in enumerate(tr_junctions):
            color = "blue" if ambulance_mode else ("orange" if accident_mode and i == 2 else ("green" if current_tr_data[i] > 70 else "orange" if current_tr_data[i] > 40 else "red"))
            g_time = get_green_time(current_tr_data[i])
            folium.CircleMarker(location=coord, radius=8+(current_tr_data[i]/4), color=color, fill=True, fill_opacity=0.9).add_to(m)
            folium.Marker(location=coord, icon=folium.DivIcon(html=f"<div style='color:white;font-weight:bold;'>{tr_names[i]}<br>{g_time}s</div>")).add_to(m)

        st_folium(m, width=1100, height=500, key="tr_map")
        
        st.subheader("📈 Traffic Trend")
        t_range = list(range(max(0, tr_hour-3), tr_hour+1))
        history = [get_traffic_logic(h, tr_manual) for h in t_range]
        st.line_chart(pd.DataFrame(history, columns=tr_names, index=t_range))
        
        st.subheader("🌱 Sustainability Impact")
        eb, ea = sum(current_tr_data) * 1.5, sum(current_tr_data) * 1.0
        cb, ca = sum(current_tr_data) * 2.0, sum(current_tr_data) * 1.3
        
        energy_saved_val = eb - ea
        fuel_saved_val = energy_saved_val * 2.35 

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("⚡ Energy Saved", f"{energy_saved_val:.1f} kWh", delta=f"{((eb-ea)/eb)*100:.1f}%")
        with sc2:
            st.metric("⛽ Fuel Saved", f"{fuel_saved_val:.1f} L")
        with sc3:
            st.metric("🌍 CO2 Reduction", f"{cb-ca:.1f} kg", delta=f"{((cb-ca)/cb)*100:.1f}%")
            
        st.bar_chart(pd.DataFrame({"Before AI": [eb, cb], "After AI": [ea, ca]}, index=["Energy Consumption", "CO2 Emissions"]))

    # ==========================================
    # 🏢 TAB 2: SMART BUILDING (RESTORED)
    # ==========================================
    with tab2:
        st.title("🏢 Smart Building System")

        def get_real_temp():
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
                data = requests.get(url).json()
                return data['main']['temp'] if data.get("cod") == 200 else None
            except: return None

        formatted_time = now_ist.strftime("%I:%M %p") 

        people = st.slider("People in Room", 0, 100, 20, key="b_people")
        real_temp = get_real_temp()
        current_temp = real_temp if real_temp else st.sidebar.slider("Manual Temp", 0, 50, 25, key="b_temp")

        ac_mode = "❄️ Power Cool" if current_temp > 30 else "🍃 Eco Mode" if current_temp > 24 else "😴 AC Off"
        
        is_dark = now_ist.hour >= 18 or now_ist.hour < 6
        if people > 0:
            light_status = "💡 Lights: ON (Occupied)"
        elif is_dark and people == 0:
            light_status = "🌙 Lights: OFF (Energy Save)"
        else:
            light_status = "☀️ Lights: OFF (Daylight)"

        st.subheader("🤖 AI Building Control")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Outdoor Temp", f"{current_temp}°C")
            st.write(f"**Current IST Time:** {formatted_time}")
        with c2:
            st.metric("AI AC Setting", ac_mode)
        with c3:
            st.metric("Smart Lighting", light_status)

        st.markdown("---")
        b_energy_saved = 130.7 if people < 50 else 45.2
        b_efficiency = 30
        
        m1,m4 = st.columns(2)
        m1.metric("⚡ Energy Saved", f"{b_energy_saved}")
        m4.metric("Efficiency", f"{b_efficiency}% ↑")
        st.markdown("---")

        st.subheader("🛡️ Security System")
        if st.toggle("Enable Security Scan", key="b_sec_final"):
            if is_dark and people > 0:
                st.error("🚨 ALERT: Unauthorized Movement Detected (Night Hours)!")
            else:
                st.success("✅ Building Secure")

        st.subheader("📊 Building Energy Consumption (24h)")
        energy_usage = pd.DataFrame({
            "HVAC Energy": np.random.randint(20, 50, 24),
            "Lighting Energy": np.random.randint(10, 30, 24)
        })
        st.line_chart(energy_usage)

        st.subheader("City-Wide Energy Heatmap")
        h_data = pd.DataFrame({'lat': [12.9784, 12.9352, 12.9698, 12.9766], 'lon': [77.6408, 77.6245, 77.7500, 77.5993], 'color': ['#FF0000', '#00FF00', '#FF0000', '#00FF00']})
        st.map(h_data, color='color', size=200)

    # ==========================================
    # 💡 TAB 3: AI STREETLIGHTS (UNTOUCHED)
    # ==========================================
    with tab3:
        st.title("💡 AI Streetlight Optimization")
        
        col_l, col_r = st.columns(2)
        with col_l:
            s_night = st.toggle("Night Time Mode", value=True, key="s_night")
            s_motion = st.toggle("Motion Detected", value=False, key="s_motion")
            s_traffic = st.slider("Road Traffic Load (%)", 0, 100, 20, key="s_tr")

        with col_r:
            if model_loaded:
                inp = pd.DataFrame([[22 if s_night else 12, 1 if s_motion else 0, s_traffic]], columns=['time', 'movement', 'traffic'])
                prediction = model.predict(inp)[0]
                st.success("🤖 AI Prediction Active")
            else:
                prediction = 10 if not s_night else (100 if s_motion else (40 + (s_traffic/2)))
                st.info("🛰️ Adaptive Optimization Active")

            st.metric("AI Brightness Level", f"{prediction:.1f}%")
            st.progress(min(1.0, prediction/100))

        st.subheader("📊 Energy Savings Graph")
        savings_data = pd.DataFrame({"Standard": [100]*5, "AI Adaptive": [30, 20, 80, 40, 25]}, index=["12AM", "2AM", "4AM", "6AM", "8AM"])
        st.area_chart(savings_data)
else:
    st.info("AI Systems Offline. Click the button above to activate the Smart City dashboard.")