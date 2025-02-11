import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import datetime
import plotly.graph_objects as go
from wordcloud import WordCloud
import regex as re
import nltk
import matplotlib.pyplot as plt

# 📌 Funktion för att ansluta till MySQL-databasen (NU MED SQLALCHEMY)
def db_connection():
    try:
        database_url = "mysql+mysqlconnector://mlg3:denmark4ever@localhost/ArtiklarDB"
        engine = create_engine(database_url)
        return engine
    except Exception as err:
        st.error(f"Database connection error: {err}")
        return None

# 📌 Hämta data från MySQL
def get_data():
    engine = db_connection()
    if engine:
        query = "SELECT * FROM News"
        df = pd.read_sql(query, engine, index_col="id")  
        
        # 🕒 Konvertera "published" till datetime och skapa en ren datumkolumn
        if "published" in df.columns:
            df["published"] = pd.to_datetime(df["published"], errors="coerce")
            df["date"] = df["published"].dt.date
        return df
    else:
        return pd.DataFrame()

# 📌 Streamlit Konfiguration
st.set_page_config(page_title="ML 4 the Win", layout="wide")
df = get_data()

# 📌 Banner överst
st.markdown("""
    <h1 style='text-align: center; background-color: #2C2C2F; color: white; padding: 15px;'>ML 4 the Win</h1>
    """, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 📌 SIDOFÄLT - Navigation & Dynamiska Filter
st.sidebar.header("🔍 Navigation & Filter")

with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Front Page", "Data", "Analysis", "Conclusion"],
        icons=["house", "database", "bar-chart", "file-text"],
        default_index=0,
    )

# 📌 Dynamiska filter - visas bara när de behövs
startdatum = datetime.date(2025, 2, 1)
slutdatum = datetime.date(2025, 2, 28)

if selected in ["Data", "Analysis"]:
    category_columns = [col for col in df.columns if col not in ["id", "title", "summary", "link", "published", "topic", "date"]]
    category_dropdown_options = ["Alla"] + category_columns
    category = st.sidebar.selectbox("Välj kategori", category_dropdown_options, key="category_filter")

    date_range = st.sidebar.date_input(
        "Välj datumintervall", 
        [startdatum, slutdatum], 
        min_value=startdatum, 
        max_value=slutdatum
    )

if selected == "Data":
    search_query = st.sidebar.text_input("Sök efter nyckelord", key="search_filter").strip().lower()
else:
    search_query = ""  # Om vi inte är på "Data", ställ in som tom sträng

# 📌 Fix: Ensure date range always has two values
if selected in ["Data", "Analysis"]:
    if len(date_range) == 1:
        start_date = date_range[0]
        end_date = date_range[0]
    elif len(date_range) == 2:
        start_date = date_range[0]
        end_date = date_range[1]
    else:
        start_date = startdatum
        end_date = slutdatum
else:
    start_date = startdatum
    end_date = slutdatum

# 📌 Filtrera datasetet endast vid behov
df_filtered = df.copy()

if selected in ["Data", "Analysis"]:
    if category != "Alla":
        df_filtered = df_filtered[df_filtered[category] == 1]
    df_filtered = df_filtered[(df_filtered["date"] >= start_date) & (df_filtered["date"] <= end_date)]

if selected == "Data" and search_query:
    df_filtered = df_filtered[
        df_filtered["title"].str.lower().str.contains(search_query, na=False) |
        df_filtered["summary"].str.lower().str.contains(search_query, na=False)
    ]

# 📌 KPI-Beräkningar (göm KPIer om "Conclusion" är vald)
if selected != "Conclusion":
    total_articles = len(df_filtered)
    articles_with_topic = (df_filtered["topic"] != "").sum()
    percentage_with_topic = (articles_with_topic / total_articles) * 100 if total_articles > 0 else 0

    kpi_template = """
        <div style="background-color: #2C2C2F; padding: 20px; border-radius: 10px; text-align: center; color: white;
            font-size: 24px; font-weight: bold; margin: 30px 5px 10px 5px; box-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);
            width: 100%; display: block;">
            <h3 style='text-align: center; font-size: 28px; font-weight: normal;'>{title}</h3>
            <p style='text-align: center; font-size: 36px; color: #FFD700; font-weight: bold;'>{value}</p>
        </div>
    """
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(kpi_template.format(title="📊 Totalt antal artiklar", value=total_articles), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_template.format(title="📝 Artiklar med ämne", value=articles_with_topic), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_template.format(title="📈 Andel med ämne (%)", value=f"{percentage_with_topic:.2f}%"), unsafe_allow_html=True)

# 📌 MENYVAL
if selected == "Front Page":
    st.subheader("📄 Dataförhandsvisning (Topp 10 rader)")
    st.dataframe(df.head(10))

elif selected == "Data":
    st.title("📊 Utforska hela datasetet")
    st.dataframe(df_filtered)

elif selected == "Analysis":
    st.title("📊 Dataanalys & Diagram")

    # 📊 Diagram 1: Antal artiklar per kategori
    if category_columns:
        articles_per_category = df_filtered[category_columns].sum().reset_index()
        articles_per_category.columns = ["Kategori", "Antal Artiklar"]

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=articles_per_category["Kategori"],
            y=articles_per_category["Antal Artiklar"],
            marker_color="#FFD700",
            text=articles_per_category["Antal Artiklar"],
            textposition="outside"
        ))
        fig1.update_layout(title="Antal artiklar per kategori", xaxis_title="Kategori", yaxis_title="Antal artiklar")
        st.plotly_chart(fig1, use_container_width=True)

    # 📊 Diagram 2: Antal artiklar per dag
    articles_per_day = df_filtered.groupby("date").size().reset_index()
    articles_per_day.columns = ["Datum", "Antal Artiklar"]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=articles_per_day["Datum"],
        y=articles_per_day["Antal Artiklar"],
        marker_color="#FFD700",
        text=articles_per_day["Antal Artiklar"],
        textposition="outside"
    ))
    fig2.update_layout(title="Antal artiklar per dag", xaxis_title="Datum", yaxis_title="Antal artiklar", xaxis=dict(range=[start_date, end_date]))
    st.plotly_chart(fig2, use_container_width=True)

    # 📈 Diagram 3: Utveckling över tid
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=articles_per_day["Datum"],
        y=articles_per_day["Antal Artiklar"],
        mode="lines+markers",
        marker=dict(color="#FFD700", size=8),
        line=dict(color="#FFD700", width=2),
        text=articles_per_day["Antal Artiklar"],
        textposition="top center"
    ))
    fig3.update_layout(title="Utveckling av antal artiklar över tid", xaxis_title="Datum", yaxis_title="Antal artiklar", xaxis=dict(range=[start_date, end_date]))
    st.plotly_chart(fig3, use_container_width=True)

    # wordcloud här plz
    st.subheader("☁️ Most Common Words in Article Topics")

    if not df_filtered.empty and "title" in df_filtered.columns:  # ✅ Check if "topic" exists
        # Combine all topics into a single text string (removes NaN values)
        text = " ".join(df_filtered["title"].dropna())  # ✅ Uses "topic" instead of "title"

        # Remove HTML tags and special characters
        text = re.sub(r"<.*?>", "", text)  # Remove HTML tags
        text = re.sub(r"[^a-zA-ZåäöÅÄÖ\s]", "", text)  # Remove special characters and numbers

        # 📌 Load Swedish stopwords
        nltk.download("stopwords")
        from nltk.corpus import stopwords  
        swedish_stopwords = set(stopwords.words("swedish"))

        # 📌 Additional words to remove
        extra_stopwords = {"img", "jpg", "png", "https", "polisen", "stockholm", "sverige", "säger", "ska", "år"}
        all_stopwords = swedish_stopwords.union(extra_stopwords)

        # 📌 Generate WordCloud
        wordcloud = WordCloud(width=1200, height=600, max_words=50, background_color="white",
                            colormap="coolwarm", stopwords=all_stopwords, 
                            contour_color="black", contour_width=1.5,
                            prefer_horizontal=0.9, font_path=None).generate(text)

        # 📌 Display WordCloud
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")  # Hide axes
        st.pyplot(fig)
    else:
        st.write("No data available or the 'topic' column is missing.")

elif selected == "Conclusion":
    st.title("📋 Slutsats")
