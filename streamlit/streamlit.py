# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load your dataset (replace with real path if needed)
@st.cache_data
def load_data():
    df = pd.read_csv("../data/clean_data.csv")  # Replace with your file
    return df

df = load_data()

st.title("Tariff Impact & Alternative Sourcing Recommendation Engine")

# --- Sidebar Inputs ---
st.sidebar.header("Input Parameters")
selected_hs_code = st.sidebar.selectbox("Select HS Code", df["hs_code"].sort_values().unique())
selected_origin = st.sidebar.selectbox("Select Current Origin Country", df["origin_country"].sort_values().unique())
# base_cost = st.sidebar.number_input("Base cost per TEU", step=100, value=1000)
# hypo_tariff = st.sidebar.number_input("Hypothetical Tariff rate", min_value=0.00, max_value=3.00)

# --- Filter & Compute ---
subset = df[(df["hs_code"] == selected_hs_code) & (df["origin_country"] == selected_origin)]

if subset.empty:
    st.warning("No matching records found. Try another HS_Code or Origin.")
else:
    tariff_rate = subset['tariff_rate'].mean()
    estimated_cost = base_cost * (1 + tariff_rate)
    origin_country = subset['country_name'].unique()[0]

    div = st.container(border=True)
    div.subheader("📦 Current Trade Snapshot")
    col1, col2, col3 = div.columns(3)
    col1.metric("HS Code:", f"{selected_hs_code}")
    col2.metric("Current Origin:", f"{origin_country.capitalize()}")
    col3.metric("Tariff Rate", f'{tariff_rate*100}%')
    col1.metric("Transit days", f'{subset['shipping_days'].mean():.1f}')
    col2.metric("Total TEU", f'{subset['TEU'].sum():.2f}')
    # col1.metric("Estimated Base Cost per TEU", f"${base_cost:,.2f}")
    # col2.metric("Cost with Tariff", f"${estimated_cost:,.2f}", delta=f"${estimated_cost - base_cost:,.2f}")

    # # --- Alternative Recommendation Logic ---
    # st.subheader("🌍 Recommended Alternative Origins")

    # # Find other countries that export this HS_Code
    # alternatives = df[(df["hs_code"] == selected_hs_code) & (df["origin_country"] != selected_origin)]

    # # Dummy data: in reality, join with geopolitics/freight info
    # alt_scores = alternatives.groupby("origin_country").agg({
    #     "TEU": "count"
    # }).reset_index().rename(columns={"TEU": "Historical_Shipments"})

    # alt_scores["Base_Cost"] = base_cost * np.random.uniform(0.9, 1.1, len(alt_scores))  #  cost
    # alt_scores["Risk_Score"] = np.random.uniform(0.2, 0.9, len(alt_scores))             #  risk
    # alt_scores["Transit_Days"] = np.random.randint(15, 45, len(alt_scores))             #  transit

    # # Weighted score (lower is better)
    # alt_scores["Score"] = (
    #     alt_scores["Base_Cost"] * 0.5 +
    #     alt_scores["Risk_Score"] * 1000 * 0.3 +
    #     alt_scores["Transit_Days"] * 0.2
    # )

    # top_alts = alt_scores.sort_values("Score").head(5)

    # st.write("Top 5 Alternative Countries (Scored on Cost, Risk, Transit Time):")
    # st.dataframe(top_alts)

    # fig = px.bar(top_alts, x="origin_country", y=["Base_Cost", "Risk_Score", "Transit_Days"],
    #              barmode="group", title="Comparison of Alternatives")
    # st.plotly_chart(fig)