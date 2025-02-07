import streamlit as st
import pyodbc
import pandas as pd

# Ange din databasanslutning
server = 'HSTRMLAPTOP'
database = 'RSS'

conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes'

# Funktion för att hämta data från databasen
def fetch_data():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Hämta kolumnnamn (för dynamisk kategorihantering)
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'RSS'")
    columns = [row[0] for row in cursor.fetchall()]
    
    # Hämta data
    query = f"SELECT * FROM RSS"
    df = pd.read_sql(query, conn)

    cursor.close()
    conn.close()
    
    return df, columns[3:]  # De första tre kolumnerna är ID, Heading och Link, resten är kategorier

# Streamlit-app
def main():
    st.title("Predikterade Nyhetsartiklar")

    data, categories = fetch_data()

    if data.empty:
        st.write("Ingen data tillgänglig.")
        return

    # Loopar genom artiklar
    for _, row in data.iterrows():
        st.subheader(row['Heading'])
        st.write(f"[Länk till artikel]({row['Link']})")
        st.write("Publicerad:", row['Date'])

        # Filtrera fram kategorier med värdet 1
        active_categories = [category for category in categories if row[category] == 1]

        if active_categories:
            st.write("Predikterade kategorier:", ", ".join(active_categories))
        else:
            st.write("Ingen kategori predikterad.")

        st.write("---")

if __name__ == "__main__":
    main()

# cd C:\workspace\ML\ML-course\Gruppuppgift\Final
# streamlit run app.py