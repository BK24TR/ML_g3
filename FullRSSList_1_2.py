"""
FullRSSList_1_2.py

This script takes in articles (posts) from RssArticles_1.py (via `posts`),
extracts the desired fields (title, summary, link, and published),
fixes data format issues (like dates), and provides the final list as 'MyTheFinalList'.

Students: 
 - Ensure your 'RssArticles_1.py' is in the same folder (or adjust imports accordingly).
 - Examine how 'posts' is structured, and fix any date format issues carefully.
"""

# 1) Import posts from RssArticles_1
from RssArticles_1 import posts  # Import the posts list from another script
#import re  # Importera regex-biblioteket
from datetime import datetime # Importera datetime-biblioteket
import pandas as pd # Importera pandas-biblioteket

# Pseudo code: 
# - create a function 'gettingNecessaryList' that loops through posts
# - extract title, summary, link, published
# - handle errors with try/except if fields are missing
# - return the collected list

def gettingNecessaryList():
    """
    This function loops through 'posts' and extracts:
      title, summary, link, published
    Then stores them in a dictionary, finally returns a list of these dictionaries.
    """
    # Pseudo code:
    #  1. Initialize an empty list (allitems)
    #  2. Loop through each 'post' in 'posts'
    #  3. Create a temp dict for each 'post'
    #  4. Extract needed keys; if missing, set to empty string
    #  5. Append the dict to the list
    #  6. Return allitems
    
# Funktion för att extrahera nödvändiga fält och hantera eventuella fel
def gettingNecessaryList(posts):
    """
    Extraherar nödvändiga fält (title, summary, link, published) från posts
    och returnerar en lista av dictionaries.
    """
    allitems = []

    for x in posts:
        try:
            tempdict = {
                "title": x.get("title", ""),
                "summary": x.get("summary", ""),
                "link": x.get("link", ""),
                "published": x.get("published", ""),
            }
            allitems.append(tempdict)
        except Exception as e:
            print(f"Error processing post: {e}")
    
    return allitems

def format_date(date_str):
    """
    Konverterar en RSS-datumsträng till formatet YYYY-MM-DD HH:MM:SS.
    """
    if not date_str or pd.isna(date_str):  # Hanterar saknade datum (None eller tom sträng)
        return None

    # Ersätt tidszonsförkortningar med motsvarande offset
    date_str = date_str.replace("GMT", "+0000")  # Om GMT används, ersätt med UTC-offset

    # Testa olika format som RSS-flöden ofta använder
    date_formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # Exempel: "Mon, 03 Feb 2025 20:27:02 +0100"
        "%Y-%m-%dT%H:%M:%S%z"       # Exempel: "2025-02-02T16:41:00+01:00"
    ]

    for fmt in date_formats:
        try:
            # Försök att parsa datumsträngen med det aktuella formatet
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")  # Standardiserat format
        except ValueError:
            continue  # Om det misslyckas, testa nästa format

    # Om inget format fungerar, skriv ut datumet för debugging
    print("Okänt format, kunde inte parsas:", date_str)
    return None


def ThefinalList(AllItemsX):
    """
    This function converts AllItemsX into a final 2D list (or list of lists),
    while ensuring that 'published' is properly formatted (YYYY-MM-DD HH:MM:SS).
    """
    # Pseudo code:
    #  1. Initialize finalList = []
    #  2. For each item (dict) in AllItemsX:
    #       a) Extract title, summary, link, published
    #       b) Parse 'published' date with multiple possible formats
    #       c) Append results as a small list [title, summary, link, published_str] to finalList
    #  3. Return finalList
    
    finalList = []

    for item in AllItemsX:
        title = item.get("title", "")
        summary = item.get("summary", "")
        link = item.get("link", "")
        published = format_date(item.get("published", ""))

        # Lägg bara till poster med giltigt datum
        if published:  # Kontrollera att datumet inte är None
            finalList.append([title, summary, link, published])
    
    return finalList

# Extraherar nödvändiga fält från 'posts'
AllItemsX = gettingNecessaryList(posts)

# 3) Create a variable that holds the final list
MyTheFinalList = ThefinalList(AllItemsX)

# Skriver ut resultatet
print(MyTheFinalList)
print(f"Antal giltiga poster: {len(MyTheFinalList)}")