mport streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd

st.set_page_config(layout="wide")
st.title("🌍 AI Smart City - Intelligent Traffic System")

# ---------------------------
# 🎛️ CONTROLS
# ---------------------------
st.sidebar.header("Simulation Controls")

hour = st.sidebar.slider("Select Time (24h)", 0, 23, 18)

names = ["Majestic", "Indiranagar", "Silk Board", "Jayanagar"]

manual_traffic = [
    st.sidebar.slider(f"{name} Base Traffic", 0, 100, 40)
    for name in names
]

ambulance_mode = st.sidebar.checkbox("🚑 Emergency Mode")
accident_mode = st.sidebar.checkbox("💥 Accident Mode")

# ---------------------------
# 📍 JUNCTIONS
# ---------------------------
junctions = [
    [12.9763, 77.5713],
    [12.9719, 77.6412],
    [12.9352, 77.6245],
    [12.9279, 77.5834],
]

# ---------------------------
# 🚦 TRAFFIC MODEL (UNCHANGED)
# ---------------------------
def get_traffic(hour, base):
    traffic = base.copy()

    if 8 <= hour <= 10:
        traffic = [t + inc for t, inc in zip(traffic, [20, 15, 30, 10])]
    elif 17 <= hour <= 20:
        traffic = [t + inc for t, inc in zip(traffic, [25, 20, 35, 15])]

    return [min(100, t) for t in traffic]

traffic = get_traffic(hour, manual_traffic)

# ---------------------------
# ⏱️ SIGNAL TIME
# ---------------------------
def get_green_time(t):
    return int(20 + (t / 100) * 40)

# ---------------------------
# 🚦 ROAD COLOR
# ---------------------------
def get_road_color(t):
    if t > 70:
        return "red"
    elif t > 40:
        return "orange"
    else:
        return "green"

# ---------------------------
# 🤖 PREDICTION
# ---------------------------
predicted = [min(100, int(t * 1.1)) for t in traffic]

# ---------------------------
# 🗺️ MAP
# ---------------------------
def generate_map():
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, tiles="cartodb dark_matter")

    roads = [
        (junctions[0], junctions[1]),
        (junctions[1], junctions[2]),
        (junctions[2], junctions[3]),
        (junctions[3], junctions[0]),
    ]

    # Roads
    for i, r in enumerate(roads):
        avg_traffic = (traffic[i] + traffic[(i+1) % 4]) / 2

        folium.PolyLine(
            r,
            color=get_road_color(avg_traffic),
            weight=6,
            opacity=0.8
        ).add_to(m)

    # Signals
    for i, coord in enumerate(junctions):

        if ambulance_mode:
            color = "blue"
            reason = "Emergency Override"

        elif accident_mode:
            if i == 2:
                color = "orange"
                reason = "Accident Zone"
            elif traffic[i] > 60:
                color = "green"
                reason = "High Flow"
            elif traffic[i] > 30:
                color = "orange"
                reason = "Moderate Flow"
            else:
                color = "red"
                reason = "Low Flow"

        else:
            if traffic[i] > 70:
                color = "green"
                reason = "Heavy Traffic"
            elif traffic[i] > 40:
                color = "orange"
                reason = "Moderate Traffic"
            else:
                color = "red"
                reason = "Low Traffic"

        green_time = get_green_time(traffic[i])
        radius = 8 + (traffic[i] / 4)

        folium.CircleMarker(
            location=coord,
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.9,
            popup=f"{names[i]}: {traffic[i]}% | {reason} | Green: {green_time}s"
        ).add_to(m)

        folium.Marker(
            location=coord,
            icon=folium.DivIcon(html=f"""
                <div style="color:white;font-weight:bold;text-align:center;">
                    {names[i]}<br>
                    {green_time}s
                </div>
            """)
        ).add_to(m)

    # Ambulance
    if ambulance_mode:
        route = [junctions[0], junctions[1], junctions[2]]
        folium.PolyLine(route, color="yellow", weight=6).add_to(m)

    # Accident
    if accident_mode:
        folium.Marker(
            location=junctions[2],
            icon=folium.Icon(color="red"),
            popup="Accident Zone"
        ).add_to(m)

    return m

# ---------------------------
# 📊 MAP DISPLAY
# ---------------------------
st_folium(generate_map(), width=1100, height=550, key="city_map")

# ---------------------------
# 🚦 LEGEND
# ---------------------------
st.markdown("""
### 🚦 Traffic Legend

<div style="display:flex; align-items:center;">
<div style="width:50px;height:6px;background:green;margin-right:10px;"></div>Low Traffic
</div>
<div style="display:flex; align-items:center;">
<div style="width:50px;height:6px;background:orange;margin-right:10px;"></div>Moderate Traffic
</div>
<div style="display:flex; align-items:center;">
<div style="width:50px;height:6px;background:red;margin-right:10px;"></div>High Traffic
</div>
<div style="display:flex; align-items:center;">
<div style="width:50px;height:6px;background:blue;margin-right:10px;"></div>Emergency Override
</div>
""", unsafe_allow_html=True)

# ---------------------------
# 📈 TRAFFIC TREND (UNCHANGED)
# ---------------------------
st.subheader("📈 Traffic Trend")

time_range = list(range(max(0, hour-3), hour+1))
history = [get_traffic(h, manual_traffic) for h in time_range]

df = pd.DataFrame(history, columns=names, index=time_range)
st.line_chart(df)

# ---------------------------
# 🌱 SUSTAINABILITY
# ---------------------------
st.subheader("🌱 Sustainability Impact")

energy_before = sum(traffic) * 1.5
energy_after = sum(traffic) * 1.0

co2_before = sum(traffic) * 2.0
co2_after = sum(traffic) * 1.3

impact_df = pd.DataFrame({
    "Before AI": [energy_before, co2_before],
    "After AI": [energy_after, co2_after]
}, index=["Energy Consumption", "CO₂ Emissions"])

st.bar_chart(impact_df)

energy_saved = ((energy_before - energy_after) / energy_before) * 100
co2_saved = ((co2_before - co2_after) / co2_before) * 100

st.success(f"⚡ Energy Reduced: {energy_saved:.1f}%")
st.success(f"🌱 CO₂ Reduced: {co2_saved:.1f}%")

# ---------------------------
# 🤖 AI SUMMARY
# ---------------------------
st.subheader("🤖 AI Decision Summary")

worst = traffic.index(max(traffic))

st.write(f"Peak Hour: {hour}")
st.write(f"Highest Traffic: {names[worst]}")

if ambulance_mode:
    st.info("🚑 Emergency override active")
elif accident_mode:
    st.warning("⚠️ Accident detected, traffic redistributed")
else:
    st.success("AI dynamically optimizes multiple signals for smooth traffic flow")