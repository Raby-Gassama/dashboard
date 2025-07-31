import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

@st.cache_data
def load_data():
    df = pd.read_csv('Transactions_data_complet.csv', parse_dates=['TransactionStartTime'])
    df['TransactionStartTime'] = pd.to_datetime(df['TransactionStartTime'], errors='coerce')
    return df

df = load_data()

st.title("Dashboard Transactions - Projet Final")

# Sidebar : filtres
min_date = df['TransactionStartTime'].min().date()
max_date = df['TransactionStartTime'].max().date()
date_range = st.sidebar.date_input("Période", [min_date, max_date])
amount_range = st.sidebar.slider(
    "Montant",
    int(df['Amount'].min()),
    int(df['Amount'].quantile(0.95)),
    (int(df['Amount'].min()), int(df['Amount'].quantile(0.95)))
)
fraud_opts = st.sidebar.multiselect(
    "Statut de fraude",
    df['FraudResult'].unique(),
    default=list(df['FraudResult'].unique())
)

df_filtered = df[
    (df['TransactionStartTime'].dt.date >= date_range[0]) &
    (df['TransactionStartTime'].dt.date <= date_range[1]) &
    (df['Amount'] >= amount_range[0]) &
    (df['Amount'] <= amount_range[1]) &
    (df['FraudResult'].isin(fraud_opts))
]

st.subheader("Aperçu des données filtrées")
st.dataframe(df_filtered.head(10))

# 1. Distribution linéaire
fig1 = px.histogram(df_filtered, x='Amount', nbins=50)
st.plotly_chart(fig1, use_container_width=True)

# 2. Distribution log
fig2 = px.histogram(df_filtered, x='Amount', nbins=50)
fig2.update_xaxes(type="log")
st.plotly_chart(fig2, use_container_width=True)

# 3. Transactions par statut de fraude
fig3 = px.histogram(df_filtered, x='FraudResult')
st.plotly_chart(fig3, use_container_width=True)

# 4. Taux de fraude par canal
fraud_rate = df_filtered.groupby(['ChannelId','FraudResult']).size().reset_index(name='Count')
fig4 = px.bar(fraud_rate, x='ChannelId', y='Count', color='FraudResult', barmode='group')
st.plotly_chart(fig4, use_container_width=True)

# 5. Heatmap de corrélation
corr = df_filtered.select_dtypes(include=np.number).corr()
fig5 = px.imshow(corr, text_auto=True)
st.plotly_chart(fig5, use_container_width=True)

# 6. Boxplot par catégorie
fig6 = px.box(df_filtered, x='ProductCategory', y='Amount')
st.plotly_chart(fig6, use_container_width=True)

# 7. Série temporelle par jour
df_filtered['Date'] = df_filtered['TransactionStartTime'].dt.date
ts = df_filtered.groupby('Date').size().reset_index(name='Count')
fig7 = px.line(ts, x='Date', y='Count')
st.plotly_chart(fig7, use_container_width=True)
