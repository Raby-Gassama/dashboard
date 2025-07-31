import streamlit as st
import pandas as pd

# Charge les données sans aucune conversion
df = pd.read_csv("Transactions_data_complet.csv")

# Affiche les noms de colonnes et les cinq premières lignes
st.write("🚀 Colonnes chargées :", list(df.columns))
st.write("🔍 Coup d’œil sur les données :", df.head())

# Maintenant seulement : convertir la date si la colonne existe
if "TransactionStartTime" in df.columns:
    df["TransactionStartTime"] = pd.to_datetime(
        df["TransactionStartTime"],
        format="%Y-%m-%dT%H:%M:%SZ",
        errors="coerce",
    )
else:
    st.error("💥 La colonne 'TransactionStartTime' est introuvable dans le CSV.")

# Titre principal
st.title("Dashboard Transactions – Projet Final")

# ─── Sidebar : filtres ─────────────────────────────────────────────────────────
min_date = df["TransactionStartTime"].min().date()
max_date = df["TransactionStartTime"].max().date()
date_range = st.sidebar.date_input(
    "Période", [min_date, max_date], min_value=min_date, max_value=max_date
)

amount_min = int(df["Amount"].min())
amount_max = int(df["Amount"].quantile(0.95))
amount_range = st.sidebar.slider(
    "Montant",
    amount_min,
    amount_max,
    (amount_min, amount_max),
)

fraud_options = list(df["FraudResult"].unique())
fraud_selected = st.sidebar.multiselect(
    "Statut de fraude", fraud_options, default=fraud_options
)

# Filtrage
mask = (
    (df["TransactionStartTime"].dt.date >= date_range[0])
    & (df["TransactionStartTime"].dt.date <= date_range[1])
    & (df["Amount"] >= amount_range[0])
    & (df["Amount"] <= amount_range[1])
    & (df["FraudResult"].isin(fraud_selected))
)
df_filtered = df[mask]

# ─── Affichage de l’aperçu ────────────────────────────────────────────────────
st.subheader("Aperçu des données filtrées")
st.dataframe(df_filtered.head(10), use_container_width=True)

# ─── 1. Distribution linéaire ────────────────────────────────────────────────
fig1 = px.histogram(
    df_filtered,
    x="Amount",
    nbins=50,
    title="Distribution des montants (linéaire)",
)
st.plotly_chart(fig1, use_container_width=True)

# ─── 2. Distribution logarithmique ────────────────────────────────────────────
fig2 = px.histogram(
    df_filtered,
    x="Amount",
    nbins=50,
    title="Distribution des montants (échelle logarithmique)",
)
fig2.update_xaxes(type="log")
st.plotly_chart(fig2, use_container_width=True)

# ─── 3. Transactions par statut de fraude ────────────────────────────────────
fig3 = px.histogram(
    df_filtered,
    x="FraudResult",
    title="Nombre de transactions par statut de fraude",
)
st.plotly_chart(fig3, use_container_width=True)

# ─── 4. Taux de fraude par canal ──────────────────────────────────────────────
fraud_rate = (
    df_filtered.groupby(["ChannelId", "FraudResult"])
    .size()
    .reset_index(name="Count")
)
fig4 = px.bar(
    fraud_rate,
    x="ChannelId",
    y="Count",
    color="FraudResult",
    barmode="group",
    title="Transactions par canal et statut de fraude",
)
st.plotly_chart(fig4, use_container_width=True)

# ─── 5. Heatmap de corrélation ───────────────────────────────────────────────
corr = df_filtered.select_dtypes(include=np.number).corr()
fig5 = px.imshow(
    corr,
    text_auto=True,
    title="Matrice de corrélation",
)
st.plotly_chart(fig5, use_container_width=True)

# ─── 6. Boxplot par catégorie de produit ────────────────────────────────────
fig6 = px.box(
    df_filtered,
    x="ProductCategory",
    y="Amount",
    title="Distribution des montants par catégorie de produit",
)
st.plotly_chart(fig6, use_container_width=True)

# ─── 7. Série temporelle journalière ─────────────────────────────────────────
df_filtered["Date"] = df_filtered["TransactionStartTime"].dt.date
ts = df_filtered.groupby("Date").size().reset_index(name="Count")
fig7 = px.line(
    ts,
    x="Date",
    y="Count",
    title="Nombre de transactions par jour",
)
st.plotly_chart(fig7, use_container_width=True)
