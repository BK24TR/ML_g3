import pyodbc
import pandas as pd
from ML_predictions import final_RSS
from BestModel import categories

# Ange din databasanslutning
server = 'HSTRMLAPTOP'
database = 'RSS'

conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes'

# Anslut till SQL Server
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Skapa tabellen om den inte finns
table_name = "RSS"

create_table_query = f"""
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}' AND xtype='U')
BEGIN
    CREATE TABLE {table_name} (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        Heading NVARCHAR(MAX),
        Link NVARCHAR(500) UNIQUE,
        Date DATETIME,
        {', '.join([f'[{category}] INT' for category in categories])}
    )
END
"""
cursor.execute(create_table_query)
conn.commit()

# Hämta befintliga länkar för att undvika dubletter
cursor.execute(f"SELECT Link FROM {table_name}")
existing_links = set(row[0] for row in cursor.fetchall())  # Skapa en set med befintliga länkar

# Filtrera bort rader som redan finns i databasen
new_rows = final_RSS[~final_RSS['Link'].isin(existing_links)]

if not new_rows.empty:
    # Spara de unika raderna i SQL Server
    for index, row in new_rows.iterrows():
        columns = ', '.join(new_rows.columns)
        placeholders = ', '.join(['?' for _ in new_rows.columns])
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            cursor.execute(insert_query, tuple(row))
        except pyodbc.IntegrityError:
            print(f"Dublett hittad, skippad: {row['Link']}")
    
    # Bekräfta ändringar
    conn.commit()
    print(f"{len(new_rows)} nya artiklar har lagts till i databasen.")

else:
    print("Inga nya artiklar att lägga till.")

# Stäng anslutningen
cursor.close()
conn.close()