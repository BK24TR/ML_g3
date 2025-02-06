import streamlit as st
import pandas as pd
import os

# Ange fil-path (använd den lösning som fungerade i Streamlit Cloud)
file_path = os.path.join(os.path.dirname(__file__), "data.csv")

# Läs in CSV-filen
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame()

# Aktivera Streamlits Dark Mode
st.set_page_config(page_title="ML av Grupp 3", layout="wide")

# Banner överst
st.markdown("""
    <h1 style='text-align: center; background-color: #444; color: white; padding: 15px;'>ML av Grupp 3</h1>
    """, unsafe_allow_html=True)

# SIDOFÄLT - Använd Streamlits inbyggda sidebar istället för en custom column
st.sidebar.header("🔍 Filter")
category = st.sidebar.selectbox("Välj kategori", ["Alla", "Politik", "Ekonomi", "Sport"], key="category_filter")
date_range = st.sidebar.date_input("Välj datumintervall", [])
search_query = st.sidebar.text_input("Sök efter nyckelord", key="search_filter")

# HUVUDSEKTION - Dela resten av ytan 50/50
col1, col2 = st.columns(2)

# Visa data om fil finns
st.subheader("📄 Dataförhandsvisning")
if not df.empty:
    st.dataframe(df.head())
else:
    st.warning("Ingen data hittades. Ladda upp en fil.")

with col1:
    st.subheader("📈 Diagram 1")
    st.write("Plats för graf eller annan analys.")

    st.subheader("📊 Tabell 1")
    st.write("Här kan en tabell visas.")

with col2:
    st.subheader("📉 Diagram 2")
    st.write("Plats för en andra graf.")

    st.subheader("📋 Tabell 2")
    st.write("Här kan en annan tabell visas.")


