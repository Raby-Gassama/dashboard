import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Configuration optionnelle
st.set_page_config(page_title="Dashboard Transactions", layout="wide")

@st.cache_data
def load_data():
    # 1) Lecture du CSV
    df = pd.read_csv("Transactions_data_complet.csv")
    # 2) Conversion de la colonne 'Date' en datetime
    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%Y-%m-%d",
        errors="coerce"
    )
    return df

# Chargement
df = load_data()

# Titre principal
st.title("Dashboard Transactions – Projet Final")

# ─── Sidebar : filtres ─────────────────────────────────────────────────────────
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Période",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date,
)

amount_min = int(df["Amount"].min())
amount_max = int(df["Amount"].quantile(0.95))
amount_range = st.sidebar.slider(
    "Montant",
    amount_min,
    amount_max,
    (amount_min, amount_max),
)

fraud_options = list(df["FraudResult"].unique()) if "FraudResult" in df.columns else []
fraud_selected = st.sidebar.multiselect(
    "Statut de fraude",
    fraud_options,
    default=fraud_options
)

# ─── Application des filtres ────────────────────────────────────────────────────
mask = (
    (df["Date"].dt.date >= date_range[0]) &
    (df["Date"].dt.date <= date_range[1]) &
    (df["Amount"] >= amount_range[0]) &
    (df["Amount"] <= amount_range[1])
)
if "FraudResult" in df.columns and fraud_selected:
    mask &= df["FraudResult"].isin(fraud_selected)

df_filtered = df[mask]

# ─── Aperçu ─────────────────────────────────────────────────────────────────────
st.subheader("Aperçu des données filtrées")
st.dataframe(df_filtered.head(10), use_container_width=True)

# ─── 1. Distribution linéaire ─────────────────────────────────────────────────
fig1 = px.histogram(
    df_filtered, x="Amount", nbins=50,
    title="Distribution des montants (linéaire)"
)
st.plotly_chart(fig1, use_container_width=True)

# ─── 2. Distribution log ───────────────────────────────────────────────────────
fig2 = px.histogram(
    df_filtered, x="Amount", nbins=50,
    title="Distribution des montants (log)"
)
fig2.update_xaxes(type="log")
st.plotly_chart(fig2, use_container_width=True)

# ─── 3. Transactions par statut de fraude (si présent) ─────────────────────────
if "FraudResult" in df_filtered.columns:
    fig3 = px.histogram(
        df_filtered, x="FraudResult",
        title="Nombre de transactions par statut de fraude"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ─── 4. Taux de fraude par canal ───────────────────────────────────────────────
if {"ChannelId", "FraudResult"}.issubset(df_filtered.columns):
    fraud_rate = (
        df_filtered.groupby(["ChannelId", "FraudResult"])
        .size()
        .reset_index(name="Count")
    )
    fig4 = px.bar(
        fraud_rate, x="ChannelId", y="Count", color="FraudResult",
        barmode="group", title="Transactions par canal et statut de fraude"
    )
    st.plotly_chart(fig4, use_container_width=True)

# ─── 5. Heatmap de corrélation ────────────────────────────────────────────────
corr = df_filtered.select_dtypes(include=np.number).corr()
fig5 = px.imshow(
    corr, text_auto=True, title="Matrice de corrélation"
)
st.plotly_chart(fig5, use_container_width=True)

# ─── 6. Boxplot par catégorie de produit ──────────────────────────────────────
if {"ProductCategory", "Amount"}.issubset(df_filtered.columns):
    fig6 = px.box(
        df_filtered, x="ProductCategory", y="Amount",
        title="Montants par catégorie de produit"
    )
    st.plotly_chart(fig6, use_container_width=True)

# ─── 7. Série temporelle journalière ──────────────────────────────────────────
ts = (
    df_filtered.groupby(df_filtered["Date"].dt.date)
    .size()
    .reset_index(name="Count")
)
fig7 = px.line(
    ts, x="Date", y="Count",
    title="Nombre de transactions par jour"
)
st.plotly_chart(fig7, use_container_width=True)
