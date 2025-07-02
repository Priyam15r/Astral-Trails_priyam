import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Set page config
st.set_page_config(page_title="Cosmic Radiation Risk Calculator", layout="wide")

# Title
st.title("Cosmic Radiation Risk Calculator & Shielding Materials Analysis")

# Sidebar inputs
st.sidebar.header("Mission Parameters")
mission_days = st.sidebar.slider("Mission Duration (days)", 1, 1000, 180)
shielding_material = st.sidebar.selectbox("Shielding Material", [
    "None", "Liquid Hydrogen", "Lithium Hydride (LiH)", "Liquid Methane", "Water",
    "Polyethylene", "Boron-loaded Polyetherimide (20%)", "Boron-loaded Polyetherimide (15%)",
    "Boron-loaded Polyetherimide (10%)", "Boron-loaded Polyetherimide (5%)", "PTFE (Teflon)",
    "Polyetherimide", "Boron-loaded Polysulfone (10%)", "Boron-loaded Polyimide (10%)",
    "Polysulfone", "Aluminum", "Polyimide (Kapton)", "Pure Epoxy",
    "Regolith/Epoxy Composite", "Lunar Regolith", "Magnesium", "Iron", "Copper", "Lead"
])

# Shielding factors (example values from NASA paper)
shielding_factors = {
    "None": 1.0,
    "Liquid Hydrogen": 0.30,
    "Lithium Hydride (LiH)": 0.35,
    "Liquid Methane": 0.38,
    "Water": 0.40,
    "Polyethylene": 0.50,
    "Boron-loaded Polyetherimide (20%)": 0.50,
    "Boron-loaded Polyetherimide (15%)": 0.51,
    "Boron-loaded Polyetherimide (10%)": 0.53,
    "Boron-loaded Polyetherimide (5%)": 0.55,
    "PTFE (Teflon)": 0.60,
    "Polyetherimide": 0.60,
    "Boron-loaded Polysulfone (10%)": 0.60,
    "Boron-loaded Polyimide (10%)": 0.62,
    "Polysulfone": 0.65,
    "Aluminum": 0.70,
    "Polyimide (Kapton)": 0.70,
    "Pure Epoxy": 0.70,
    "Regolith/Epoxy Composite": 0.72,
    "Lunar Regolith": 0.75,
    "Magnesium": 0.78,
    "Iron": 0.80,
    "Copper": 0.85,
    "Lead": 0.95
}

# Get selected shielding factor
attenuation = shielding_factors[shielding_material]

# Define base dose rate (example: 0.5 mSv/day in space)
base_daily_dose = 0.5  # mSv/day

# Calculate total dose
total_dose = base_daily_dose * attenuation * mission_days

# Create data for plotting shielding factor vs days
days_array = np.linspace(1, 1000, 1000)
shielding_vs_days = []
for material, factor in shielding_factors.items():
    # Assume linear variation for demonstration; real data may differ
    # For simplicity, assume shielding factor remains constant over days
    shielding_vs_days.append({
        'material': material,
        'days': days_array,
        'shielding_factor': np.full_like(days_array, factor)
    })

# Plot shielding factor vs days
st.subheader("Shielding Factor vs Mission Duration")
fig1 = go.Figure()
for data in shielding_vs_days:
    fig1.add_trace(go.Scatter(
        x=data['days'],
        y=data['shielding_factor'],
        mode='lines',
        name=data['material'],
        opacity=0.3 if data['material'] != shielding_material else 1,
        line=dict(width=2 if data['material'] == shielding_material else 1)
    ))
# Highlight selected material
selected_factor = shielding_factors[shielding_material]
fig1.add_trace(go.Scatter(
    x=[mission_days],
    y=[selected_factor],
    mode='markers',
    marker=dict(color='red', size=12, symbol='circle'),
    name='Selected Material'
))
fig1.update_layout(
    height=500,
    xaxis_title='Mission Duration (days)',
    yaxis_title='Shielding Factor',
    legend_title='Materials',
    showlegend=False
)
st.plotly_chart(fig1, use_container_width=True)

# Plot total dose vs days for selected material
st.subheader("Estimated Total Dose vs Mission Duration")
dose_vs_days = base_daily_dose * attenuation * days_array
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=days_array,
    y=dose_vs_days,
    mode='lines',
    name=shielding_material
))
# Highlight selected mission duration
selected_dose = total_dose
fig2.add_trace(go.Scatter(
    x=[mission_days],
    y=[selected_dose],
    mode='markers',
    marker=dict(color='red', size=12, symbol='circle'),
    name='Selected Duration'
))
fig2.update_layout(
    height=500,
    xaxis_title='Mission Duration (days)',
    yaxis_title='Total Dose (mSv)',
    showlegend=False
)
st.plotly_chart(fig2, use_container_width=True)

# Display key results
st.metric("Estimated Total Dose (mSv)", f"{total_dose:.2f}")
st.metric("Selected Shielding Material", shielding_material)
st.caption("Note: Dose increases linearly with mission duration and is mitigated by shielding.")

# Optional: Add real-time space weather data fetch (placeholder)
st.sidebar.header("Space Weather Data")
try:
    # Placeholder for real API call
    st.sidebar.info("Fetching real-time space weather data... (not implemented)")
except:
    st.sidebar.warning("Unable to fetch space weather data.")

# End of app
