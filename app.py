# cosmic_radiation_app.py
"""
Streamlit app: Cosmic Radiation Risk Calculator
• Calculates cumulative space-radiation dose as a function of mission length
• Lets users choose from 24 shielding materials (NASA TP-3473 + recent studies)
• Plots
    1. Shielding factor vs. mission duration (all materials, highlighted day)
    2. Total dose vs. mission duration for chosen material (highlighted day)
"""

import streamlit as st
import requests, json, time
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ════════════════════════════════════════════════════════════════════════════
# 1. Page Config & Title
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Cosmic Radiation Risk Calculator",
                   layout="centered",
                   initial_sidebar_state="expanded")
st.title("☢️ Cosmic Radiation Risk Calculator")

# ════════════════════════════════════════════════════════════════════════════
# 2. User Inputs
# ════════════════════════════════════════════════════════════════════════════
MAX_DAYS = 1000
mission_days = st.slider("Mission Duration (days)", 1, MAX_DAYS, 180,
                         help="Total time spent in deep space")

# NASA-derived & literature-derived attenuation factors (fraction of unshielded dose)
SHIELD_FACTORS = {
    "None"                                        : 1.00,
    "Liquid Hydrogen"                             : 0.30,
    "Lithium Hydride (LiH)"                       : 0.35,
    "Liquid Methane"                              : 0.38,
    "Water"                                       : 0.40,
    "Polyethylene"                                : 0.50,
    "B-PEI (Boron-PEI 20 wt %)"                   : 0.50,
    "B-PEI (15 wt %)"                             : 0.51,
    "B-PEI (10 wt %)"                             : 0.53,
    "B-PEI (5 wt %)"                              : 0.55,
    "PTFE (Teflon)"                               : 0.60,
    "Polyetherimide"                              : 0.60,
    "B-Polysulfone (10 wt %)"                     : 0.60,
    "B-Polyimide (10 wt %)"                       : 0.62,
    "Polysulfone"                                 : 0.65,
    "Aluminum"                                    : 0.70,
    "Polyimide (Kapton)"                          : 0.70,
    "Pure Epoxy"                                  : 0.70,
    "Regolith/Epoxy Composite"                    : 0.72,
    "Lunar Regolith"                              : 0.75,
    "Magnesium"                                   : 0.78,
    "Iron"                                        : 0.80,
    "Copper"                                      : 0.85,
    "Lead"                                        : 0.95,
}
material_names = list(SHIELD_FACTORS.keys())
material = st.selectbox("Shielding Material", material_names, index=material_names.index("Polyethylene"))

# ════════════════════════════════════════════════════════════════════════════
# 3. Real-Time Proton Flux (NOAA GOES)
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def get_live_flux():
    url = "https://services.swpc.noaa.gov/json/goes/primary/differential-proton-flux-1-day.json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        latest_flux = float(data[-1]["flux"])      # protons cm⁻² s⁻¹ sr⁻¹ (≥10 MeV)
        return latest_flux
    except Exception:
        return None  # fallback handled below

proton_flux = get_live_flux()
if proton_flux is None:
    proton_flux = 100.0
    st.warning("⚠️ Live proton-flux fetch failed – using fallback 100 p cm⁻² s⁻¹ sr⁻¹")
else:
    st.success(f"🌐 Live Proton Flux (≥10 MeV): {proton_flux: .2e} p cm⁻² s⁻¹ sr⁻¹")

# ════════════════════════════════════════════════════════════════════════════
# 4. Dose Model
# ════════════════════════════════════════════════════════════════════════════
# Empirical scale-factor converts proton flux to deep-space mixed-field dose (mSv/day)
BASE_DOSE_RATE = proton_flux * 5.0e-5     # tunable constant → ~0.5 mSv/day for quiet sun
attenuation = SHIELD_FACTORS[material]
daily_dose      = BASE_DOSE_RATE * attenuation
total_dose      = daily_dose * mission_days            # mSv
risk_percent    = (total_dose / 1000) * 5.0            # 5 % per Sv (ICRP-60)

col1, col2, col3 = st.columns(3)
col1.metric("📅 Days", f"{mission_days}")
col2.metric("☢ Total Dose (mSv)", f"{total_dose: .2f}")
col3.metric("⚕ Estimated ↑Cancer Risk", f"{risk_percent: .2f} %")

st.caption("Dose model: GCR-dominated, linear scaling with mission length; ICRP-60 5 % ERR per 1 Sv.")

# ════════════════════════════════════════════════════════════════════════════
# 5. Plot – Shielding Factor vs. Mission Duration
# ════════════════════════════════════════════════════════════════════════════
days_axis = np.arange(1, MAX_DAYS + 1)
fig_sf = go.Figure()
for mat, factor in SHIELD_FACTORS.items():
    fig_sf.add_trace(go.Scatter(x=days_axis,
                                y=np.full_like(days_axis, factor),
                                mode="lines",
                                name=mat,
                                line=dict(width=1)))
# Highlight selected day
fig_sf.add_shape(type="line", x0=mission_days, x1=mission_days,
                 y0=0, y1=1.05, yref="y", line=dict(color="red", dash="dash"))
fig_sf.update_layout(title="Shielding Factor vs. Mission Duration",
                     xaxis_title="Mission Duration (days)",
                     yaxis_title="Shielding Factor (lower = better)",
                     height=450, showlegend=False)
st.plotly_chart(fig_sf, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 6. Plot – Total Dose vs. Mission Duration (Selected Material)
# ════════════════════════════════════════════════════════════════════════════
dose_curve = daily_dose / attenuation * np.array(list(SHIELD_FACTORS.values())[0])  # ensure consistent scaling
dose_curve = (BASE_DOSE_RATE * attenuation) * days_axis  # mSv over time for selected material

fig_td = go.Figure()
fig_td.add_trace(go.Scatter(x=days_axis, y=dose_curve,
                            mode="lines", name=material,
                            line=dict(color="royalblue", width=3)))
fig_td.add_trace(go.Scatter(x=[mission_days], y=[total_dose],
                            mode="markers", name="Current selection",
                            marker=dict(color="red", size=10)))
fig_td.update_layout(title=f"Total Dose vs. Mission Duration ({material})",
                     xaxis_title="Mission Duration (days)",
                     yaxis_title="Cumulative Dose (mSv)",
                     height=450, showlegend=False)
st.plotly_chart(fig_td, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 7. Data Download
# ════════════════════════════════════════════════════════════════════════════
csv_df = pd.DataFrame({
    "Days": days_axis,
    f"Total Dose [{material}] (mSv)": dose_curve
})
st.download_button("💾 Download dose curve CSV",
                   data=csv_df.to_csv(index=False),
                   file_name=f"dose_curve_{material.replace(' ','_')}.csv",
                   mime="text/csv")

# ════════════════════════════════════════════════════════════════════════════
# 8. Footer
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.caption("Source material attenuation factors compiled from NASA TP-3473 and subsequent peer-reviewed shielding studies (2004-2024). "
           "App written in Python • Streamlit • Plotly.")
