import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px
import re
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud

# --- Databasanslutning ---
server = 'HSTRMLAPTOP'
database = 'RSS'
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes'

# --- Funktion för att hämta data ---
@st.cache_data
def fetch_data():
    conn = pyodbc.connect(conn_str)
    query = "SELECT * FROM RSS"
    df = pd.read_sql(query, conn)
    conn.close()

    # Omvandlar "Date" till datetime om den finns i datan
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])

    return df

# --- Streamlit-app ---
st.set_page_config(page_title="ML 4 the Win", layout="wide", page_icon="📰")

# --- Hämta data ---
data = fetch_data()

# --- Extrahera kategorier från datasetet (exkludera ID, Heading, Link, Date) ---
excluded_columns = ["ID", "Heading", "Link", "Date"]
category_columns = [col for col in data.columns if col not in excluded_columns]

# --- SIDEBAR: Filtrering ---
st.sidebar.header("🎯 Filtrera artiklar")

# 📌 **Kategori-filter**
selected_category = st.sidebar.selectbox("Välj kategori", ["Alla"] + category_columns)

# 📌 **Datumfilter som drop-down med unika datum**
if "Date" in data.columns and not data.empty:
    unique_dates = sorted(data["Date"].dt.date.unique(), reverse=True)  # Sortera i fallande ordning (senaste först)
    selected_dates = st.sidebar.multiselect("Välj datum", unique_dates, default=unique_dates[:1])  # Förvalt senaste datumet

    # Filtrera på valda datum
    if selected_dates:
        data = data[data["Date"].dt.date.isin(selected_dates)]

# 📌 **Filtrera på kategori**
if selected_category != "Alla":
    data = data[data[selected_category] == 1]


# --- Lägg till radnummer ---
data.reset_index(inplace=True)
data.rename(columns={"index": "Row"}, inplace=True)

# --- Beräkna statistik ---
total_articles = len(data)
articles_with_topic = data[category_columns].sum(axis=1).gt(0).sum()
percentage_with_topic = (articles_with_topic / total_articles * 100) if total_articles > 0 else 0

# --- Visa tre informationsboxar ---
st.markdown("## ML 4 the Win")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📰 Totalt antal artiklar")
    st.markdown(f"<h2 style='text-align: center; color: yellow;'>{total_articles}</h2>", unsafe_allow_html=True)

with col2:
    st.markdown("#### 📑 Antal artiklar med ämne")
    st.markdown(f"<h2 style='text-align: center; color: yellow;'>{articles_with_topic}</h2>", unsafe_allow_html=True)

with col3:
    st.markdown("#### 📊 Andel med ämne i %")
    st.markdown(f"<h2 style='text-align: center; color: yellow;'>{percentage_with_topic:.2f}%</h2>", unsafe_allow_html=True)

st.write("---")

# --- Visa filtrerad data i en scrollbox med HTML-tabell ---
st.subheader("📑 Filtrerad lista över artiklar")

# Begränsa kolumnbredd för "Heading" och "Link"
columns_to_display = ["Row", "Heading", "Link", "Date"] + category_columns
data_to_show = data[columns_to_display]

# Skapa HTML-tabell med scrollbox
html_table = """
<style>
    .scroll-box {
        max-height: 500px;
        overflow-y: scroll;
        border: 1px solid #ddd;
        padding: 10px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #444;
        color: white;
        position: sticky;
        top: 0;
    }
    td:nth-child(2) { /* Heading */
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    td:nth-child(3) { /* Link */
        max-width: 200px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    td:nth-child(4) { /* Date */
        max-width: 150px;
        white-space: nowrap;
    }
</style>
<div class="scroll-box">
<table>
    <tr>
        <th>#</th>
        <th>Heading</th>
        <th>Link</th>
        <th>Date</th>
"""
# Lägg till kolumnnamn för kategorier
for cat in category_columns:
    html_table += f"<th>{cat}</th>"
html_table += "</tr>"

# Lägg till data i tabellen
for _, row in data_to_show.iterrows():
    html_table += "<tr>"
    html_table += f"<td>{row['Row']}</td>"
    html_table += f"<td>{row['Heading']}</td>"
    html_table += f"<td><a href='{row['Link']}' target='_blank'>{row['Link']}</a></td>"
    html_table += f"<td>{row['Date']}</td>"
    for cat in category_columns:
        html_table += f"<td>{row[cat]}</td>"
    html_table += "</tr>"

html_table += "</table></div>"

# Visa HTML-tabellen i Streamlit
st.markdown(html_table, unsafe_allow_html=True)

# --- Stapeldiagram: Antal artiklar per kategori ---
st.subheader("📊 Antal artiklar per kategori")

category_counts = data[category_columns].sum().reset_index()
category_counts.columns = ["Kategori", "Antal artiklar"]
category_counts = category_counts[category_counts["Antal artiklar"] > 0]

fig = px.bar(category_counts, x="Kategori", y="Antal artiklar", text="Antal artiklar",
             color_discrete_sequence=["yellow"], labels={"Kategori": "Kategori", "Antal artiklar": "Antal artiklar"})

st.plotly_chart(fig, use_container_width=True)

# --- Tidslinje: Antal artiklar per dag ---
st.subheader("📈 Antal artiklar per dag")

daily_counts = data.groupby(data["Date"].dt.date).size().reset_index(name="Antal artiklar")

if not daily_counts.empty:
    min_display_date = daily_counts["Date"].max() - pd.Timedelta(days=7)  # Visa senaste 7 dagarna
    daily_counts = daily_counts[daily_counts["Date"] >= min_display_date]

fig2 = px.line(daily_counts, x="Date", y="Antal artiklar", markers=True,
               labels={"Date": "Datum", "Antal artiklar": "Antal artiklar"},
               title="Utveckling av antal artiklar över tid")

fig2.update_xaxes(type="category")

st.plotly_chart(fig2, use_container_width=True)

# --- Word Cloud: Vanliga ord i artikeltitlar ---
st.subheader("☁️ Vanligaste orden i artikeltitlar")

if not data.empty:
    # Hämta alla titlar och slå ihop till en textsträng
    text = " ".join(data["Heading"].dropna())

    # Ta bort HTML-taggar och specialtecken
    text = re.sub(r"<.*?>", "", text)  # Tar bort HTML-taggar
    text = re.sub(r"[^a-zA-ZåäöÅÄÖ\s]", "", text)  # Tar bort specialtecken och siffror

    # Ladda svenska stoppord
    nltk.download("stopwords")
    swedish_stopwords = set(stopwords.words("swedish"))

    # Lägg till egna irrelevanta ord att filtrera bort
    extra_stopwords = {"img", "jpg", "png", "https", "polisen", "stockholm", "sverige", "säger", "ska", "år"}
    all_stopwords = swedish_stopwords.union(extra_stopwords)

    # Skapa Word Cloud med fler ord och bättre layout
    wordcloud = WordCloud(width=1200, height=600, max_words=50, background_color="white",
                          colormap="coolwarm", stopwords=all_stopwords, 
                          contour_color="black", contour_width=1.5,
                          prefer_horizontal=0.9, font_path=None).generate(text)

    # Visa Word Cloud
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")  # Tar bort axlarna
    st.pyplot(fig)
else:
    st.write("Ingen data tillgänglig för att skapa ett Word Cloud.")

# cd C:\workspace\ML\ML_g3\Gruppuppgift
# streamlit run app.py