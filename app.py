import streamlit as st
import requests
import numpy as np

st.set_page_config(page_title="Radiation Risk Calculator", layout="centered")

st.title("Cosmic Radiation Risk Calculator")

# Inputs
mission_days = st.slider("Mission Duration (days)", 1, 1000, 180)
#shielding_material = st.selectbox("Shielding Material", ["None","Liquid Hydrogen", "Aluminum", "Polyethylene","Water", ])
shielding_material = st.selectbox("Shielding Material", [
    "None",
    "Liquid Hydrogen",
    "Lithium Hydride (LiH)",
    "Liquid Methane",
    "Water",
    "Polyethylene",
    "B-PEI (Boron-PEI 20 wt %)",
    "B-PEI (15 wt %)",
    "B-PEI (10 wt %)",
    "B-PEI (5 wt %)",
    "PTFE (Teflon)",
    "Polyetherimide",
    "B-Polysulfone (10 wt %)",
    "B-Polyimide (10 wt %)",
    "Polysulfone",
    "Aluminum",
    "Polyimide (Kapton)",
    "Pure Epoxy",
    "Regolith/Epoxy Composite",
    "Lunar Regolith",
    "Magnesium",
    "Iron",
    "Copper",
    "Lead"
])


# Real-time proton flux from NOAA
url = "https://services.swpc.noaa.gov/json/goes/primary/differential-proton-flux-1-day.json"

try:
    data = requests.get(url).json()
    flux = float(data[-1]['flux'])  # protons/cm²/s/sr
    st.success(f"Live Proton Flux (≥10 MeV): {flux:.2e} protons/cm²/s/sr")
except:
    flux = 100  # fallback if API fails
    st.warning("Unable to fetch live data. Using default flux: 100 p/cm²/s/sr")

# Simplified dose model
base_dose_per_day = flux * 0.00005  # empirical approximation
#shield_factors = {'None': 1.0, 'Aluminum': 0.7, 'Polyethylene': 0.5}
shield_factors = {
    'None': 1.0,
    'Liquid Hydrogen': 0.30,
    'Lithium Hydride (LiH)': 0.35,
    'Liquid Methane': 0.38,
    'Water': 0.40,
    'Polyethylene': 0.50,
    'B-PEI (Boron-PEI 20 wt %)': 0.50,
    'B-PEI (15 wt %)': 0.51,
    'B-PEI (10 wt %)': 0.53,
    'B-PEI (5 wt %)': 0.55,
    'PTFE (Teflon)': 0.60,
    'Polyetherimide': 0.60,
    'B-Polysulfone (10 wt %)': 0.60,
    'B-Polyimide (10 wt %)': 0.62,
    'Polysulfone': 0.65,
    'Aluminum': 0.70,
    'Polyimide (Kapton)': 0.70,
    'Pure Epoxy': 0.70,
    'Regolith/Epoxy Composite': 0.72,
    'Lunar Regolith': 0.75,
    'Magnesium': 0.78,
    'Iron': 0.80,
    'Copper': 0.85,
    'Lead': 0.95
}
daily_dose = base_dose_per_day * shield_factors[shielding_material]
total_dose = daily_dose * mission_days  # in mSv

# Cancer risk estimate
risk_percent = (total_dose / 1000) * 5  # linear ERR model

st.metric("☢ Estimated Total Dose (mSv)", f"{total_dose:.2f}")
st.metric("⚠ Estimated Cancer Risk", f"{risk_percent:.2f} %")

st.caption("ICRP model: 5% risk increase per 1 Sv of exposure. Not for clinical use.")
