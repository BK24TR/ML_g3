import feedparser
import pandas as pd
from datetime import datetime

RSS_URLS = ['http://www.dn.se/nyheter/m/rss/',
            'https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt/', 'https://feeds.expressen.se/nyheter/',
            'http://www.svd.se/?service=rss', 'http://api.sr.se/api/rss/program/83?format=145',
            'http://www.svt.se/nyheter/rss.xml'
            ]


def fetch_posts():
    posts = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            article = {
                'Heading': entry.get('title', '') + '. ' + entry.get('summary', ''),
                'Link': entry.get('link'),
                'Date': format_date(entry.get('pubDate', entry.get('updated')))  # Använd förbättrad funktion
            }
            posts.append(article)

    df = pd.DataFrame(posts)
    return df


def format_date(date_str):
    """Konverterar en RSS-datumsträng till formatet YYYY-MM-DD HH:MM:SS."""
    if not date_str or pd.isna(date_str):  # Hanterar saknade datum (None eller NaN)
        return None

    # Ersätt tidszonsförkortningar med motsvarande offset
    date_str = date_str.replace("GMT", "+0000")  # Om GMT används, ersätt med UTC-offset

    # Testa olika format som RSS-flöden ofta använder
    date_formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # Exempel: "Sun, 02 Feb 2025 15:32:14 +0100"
        "%Y-%m-%dT%H:%M:%S%z"        # Exempel: "2025-02-02T16:41:00+01:00"
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")  # Standardiserat format
        except ValueError:
            continue  # Om det misslyckas, testa nästa format

    # Om inget format fungerar, skriv ut datumet för debugging
    print("Okänt format, kunde inte parsas:", date_str)
    return None


def main():
    df = fetch_posts()
    print(df.head())

if __name__ == "__main__":
    main()
    