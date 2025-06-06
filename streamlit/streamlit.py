# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import StandardScaler

# IMPORTANT: This must be the first Streamlit command in your script
st.set_page_config(layout="wide")

# Load your dataset (replace with real path if needed)
@st.cache_data
def load_data():
    df = pd.read_csv("../data/clean_data.csv")  # Replace with your file
    return df

df = load_data()

st.title(":material/finance_mode: :blue[Analogistics]")
st.subheader("*:orange[Smarter] Supply Chains, :orange[Smarter] Decisions*")


# --- Sidebar Inputs ---
st.sidebar.header("Current Supply Parameters")
selected_hs_code = st.sidebar.selectbox("Select HS Code", df["hs_code"].sort_values().unique())
selected_origin = st.sidebar.selectbox("Select Current Origin Country", df["origin_country"].sort_values().unique())
base_cost = st.sidebar.number_input("Base cost per TEU", step=100, value=1000)
with st.sidebar.form('Weights'):
    st.header("Weights for alternative scoring")
    w_teu = st.number_input('TEU shipments', min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    w_tariff = st.number_input('Tariff Rate', min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    w_ship_time = st.number_input('Transit Time', min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    w_wgi = st.number_input('Governance Indicator (WGI)', min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    submitted = st.form_submit_button("Update Weights")

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
    col3.metric("Tariff Rate", f'{tariff_rate*100:.2f}%')
    col1.metric("Transit days", f'{subset['shipping_days'].mean():.1f}')
    col2.metric("Total TEU", f'{subset['TEU'].sum():.2f}')
    col3.metric("WGI average", f'{np.mean(subset[['control_corruption', 'govt_effectiveness','pol_stability_absence_violence',
                                                 'rule_law', 'reg_qual','voice_accountability']].mean()):.2f}')
    col1.metric("Cost with Tariff", f"${estimated_cost:,.2f}", delta=f"${estimated_cost - base_cost:,.2f}")

    # --- Alternative Recommendation Logic ---
    st.subheader("🌍 Recommended Alternative Origins")

    # Find other countries that export this HS_Code
    alternatives = df[(df["hs_code"] == selected_hs_code) & (df["origin_country"] != selected_origin)]

    # Dummy data: in reality, join with geopolitics/freight info
    alt_scores = alternatives.groupby("origin_country").agg({
        "TEU": "sum"
    }).reset_index().rename(columns={"TEU": "TEU shipments"})

    alt_scores["Tariff Rate"] = alternatives.groupby('origin_country')['tariff_rate'].mean().reset_index()['tariff_rate']
    alt_scores["Transit Days"] = alternatives.groupby('origin_country')['shipping_days'].mean().reset_index()['shipping_days']
    alt_scores["WGI average"] = np.mean(alternatives.groupby('origin_country')[['control_corruption', 'govt_effectiveness',
       'pol_stability_absence_violence', 'rule_law', 'reg_qual',
       'voice_accountability']].mean(), axis=1).reset_index()[0]

    # Normalize values for scoring
    alt_scores['TEU shipments_n'] = StandardScaler().fit_transform(alt_scores[['TEU shipments']])
    alt_scores['Tariff Rate_n'] = StandardScaler().fit_transform(alt_scores[['Tariff Rate']])
    alt_scores['Transit Days_n'] = StandardScaler().fit_transform(alt_scores[['Transit Days']])
    alt_scores['WGI average_n'] = StandardScaler().fit_transform(alt_scores[['WGI average']])

    # Weighted score (Higher is better)
    sum_score = w_teu + w_tariff + w_ship_time + w_wgi
    user_weights = [w_teu, w_tariff, w_ship_time, w_wgi]
    norm_weights = [0,0,0,0]
    for i, w in enumerate(user_weights):
        norm_weights[i] = w/sum_score

    alt_scores["Score"] = (
        alt_scores["TEU shipments_n"] * norm_weights[0] 
        - alt_scores["Tariff Rate_n"] * norm_weights[1] 
        - alt_scores["Transit Days_n"] * norm_weights[2]
        + alt_scores["WGI average_n"] * norm_weights[3]
    )*100

    with st.popover("Score calculation"):
        st.write("The score is calculated through a weighted sum of the z-score normalized values of\
                  TEU Shipments, Tariff Rate, Transit days and WGI average. \
                 \nTariff Rate and Transit days are negated to apply \"*Higher is Better*\" for scoring consistency.")
    top_alts = alt_scores[['origin_country','TEU shipments','Tariff Rate','Transit Days','WGI average','Score']].sort_values("Score", ascending=False).head(5)
    st.dataframe(top_alts, hide_index=True)

    st.subheader('Comparison of Alternatives')
    colz, cola, colb, colc, cold = st.columns(5)
    fig_teu = px.bar(top_alts, x='origin_country', y='TEU shipments', title='TEU shipments (+)', color_discrete_sequence=['#2C5F8C'])
    fig_teu.update_yaxes(title_text='')
    fig_teu.update_xaxes(title_text='')
    cola.plotly_chart(fig_teu)

    fig_wgi = px.bar(top_alts, x='origin_country', y='WGI average', title='WGI average (+)', color_discrete_sequence=['#2C5F8C'])
    fig_wgi.update_yaxes(title_text='')
    fig_wgi.update_xaxes(title_text='')
    colb.plotly_chart(fig_wgi)

    fig_tariff = px.bar(top_alts, x='origin_country', y='Tariff Rate', title='Tariff Rate (-)', color_discrete_sequence=['#A60000'])
    fig_tariff.update_yaxes(title_text='')
    fig_tariff.update_xaxes(title_text='')
    colc.plotly_chart(fig_tariff)

    fig_transit = px.bar(top_alts, x='origin_country', y='Transit Days', title='Transit Days (-)', color_discrete_sequence=['#A60000'])
    fig_transit.update_yaxes(title_text='')
    fig_transit.update_xaxes(title_text='')
    cold.plotly_chart(fig_transit)

    fig_score = px.bar(top_alts, x='origin_country', y='Score', title='Score (+)', color_discrete_sequence=['#228B22'])
    fig_score.update_yaxes(title_text='')
    fig_score.update_xaxes(title_text='')
    colz.plotly_chart(fig_score)