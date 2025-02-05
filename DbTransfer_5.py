"""
DbTransfer_5.py

This script will:
  - Import the final structured/validated data (e.g., `validDict`) from MLModelReturns_4.py
  - Connect to a MySQL database
  - Insert each record into a table (e.g., `news`) with columns: (title, summary, link, published, topic).

Students:
 - Fill out the pseudo code to connect to the DB, handle potential errors,
   and insert data in a loop or with executemany.
"""

import MLModelReturns_4 
import mysql.connector
import pickle

# Ladda validDict från pickle-filen
with open("validDict.pkl", "rb") as file:
    validDict = pickle.load(file)

def db_connection():
    """
    Skapa och returnera en databasanslutning.
    """
    try:
        cnxn = mysql.connector.connect(
            host="localhost",  # Databasvärd
            user="root",       # Användarnamn
            password="dinmamma",  # Lösenord
            database="ArtiklarDB"  # Databasnamn
        )
        print("Connected to the database.")
        return cnxn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def article_exists(link, cnxn):
    """
    Kontrollera om en artikel med samma länk redan finns i databasen.
    Args:
        link (str): Artikellänken att kontrollera.
        cnxn: Databasanslutningen.
    Returns:
        bool: True om artikeln finns, annars False.
    """
    cursor = cnxn.cursor()
    query = "SELECT COUNT(*) FROM news WHERE link = %s"
    cursor.execute(query, (link,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] > 0

def insert_data(data, cnxn):
    """
    Infogar nya data i tabellen 'news' och undviker dubbletter.
    """
    cursor = cnxn.cursor()
    insert_sql = """
    INSERT INTO news (
        title, summary, link, published, topic, politik, utbildning, religion,
        miljo, ekonomi, livsstilfritt, samhallekonflikter, halsa, idrott, vetenskapteknik
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    data_tuples = []
    for item in data:
        if not article_exists(item['link'], cnxn):  # Kontrollera om artikeln redan finns
            categories = item['topic']
            topic_string = ",".join(categories)  # Omvandla listan till en kommaseparerad sträng
            data_tuples.append((
                item['title'], item['summary'], item['link'], item['published'], topic_string,
                1 if 'Politik' in categories else 0,
                1 if 'Utbildning' in categories else 0,
                1 if 'Religion' in categories else 0,
                1 if 'Miljo' in categories else 0,
                1 if 'Ekonomi' in categories else 0,
                1 if 'LivsstilFritt' in categories else 0,
                1 if 'SamhalleKonflikter' in categories else 0,
                1 if 'Halsa' in categories else 0,
                1 if 'Idrott' in categories else 0,
                1 if 'VetenskapTeknik' in categories else 0
            ))

    try:
        if data_tuples:  # Kontrollera att det finns nya data att lägga till
            cursor.executemany(insert_sql, data_tuples)
            cnxn.commit()
            print(f"{cursor.rowcount} nya rader har lagts till i databasen.")
        else:
            print("Inga nya artiklar att lägga till.")
    except mysql.connector.Error as err:
        print(f"Fel vid insättning av data: {err}")
    finally:
        cursor.close()

def main():
    # Anslut till databasen
    cnxn = db_connection()
    if cnxn:
        # Infoga nya data
        insert_data(validDict, cnxn)
        cnxn.close()
        print("Databasanvändning klar.")
    else:
        print("Ingen databasanslutning kunde etableras.")

if __name__ == "__main__":
    main()
