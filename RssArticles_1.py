import feedparser  # Make sure feedparser is installed: pip install feedparser

# List of RSS feed URLs
RSS_URLS = [
    'http://www.dn.se/nyheter/m/rss/',
    'https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt/',
    'https://feeds.expressen.se/nyheter/',
    'http://www.svd.se/?service=rss',
    'http://api.sr.se/api/rss/program/83?format=145',
    'http://www.svt.se/nyheter/rss.xml'
]

# Create an empty list to store articles
posts = []

# Loop through RSS feed URLs and fetch articles
for url in RSS_URLS:
    try:
        # Parse the RSS feed
        feed = feedparser.parse(url)

        # Loop through each entry (article) in the feed
        for entry in feed.entries:
            # Extract raw data and append to the posts list
            article = {
                'title': entry.get('title', ""),  # Store raw title or empty string
                'summary': entry.get('summary', ""),  # Store raw summary or empty string
                'link': entry.get('link', ""),  # Store link or empty string
                'published': entry.get('published', "")  # Store published date or empty string
            }
            posts.append(article)
    except Exception as e:
        print(f"Error parsing URL {url}: {e}")

# # -------------------- Optional Verification --------------------
# ##################### Extracting the Data ##################
# def OnlyTitlesAndSummariesWithExtras():
#     """
#     This function iterates through 'posts' and creates a new list of dictionaries,
#     each containing 'title', 'summary', 'link', and 'published'. If any key is missing,
#     replace it with an empty string.
#     """
#     all_data = []
    
#     for x in posts:
#         tempdict = {
#             "title": x.get("title", ""),
#             "summary": x.get("summary", ""),
#             "link": x.get("link", ""),
#             "published": x.get("published", "")
#         }
#         all_data.append(tempdict)
    
#     return all_data


# def TitleSummaryLinkPublishedList(all_data):
#     """
#     This function creates a nested list, where each inner list contains
#     'title', 'summary', 'link', and 'published' as a combined string.
#     """
#     final_list = []
    
#     for item in all_data:
#         combined = f"{item['title']} | {item['summary']} | {item['link']} | {item['published']}"
#         final_list.append([combined])
    
#     return final_list


# def PrintDeposit(final_list):
#     """
#     This function flattens the list returned by TitleSummaryLinkPublishedList into a
#     single list. That means if final_list = [["Item1"], ["Item2"]],
#     we want flattened_list = ["Item1", "Item2"].
#     """
#     flattened_list = []
    
#     for item in final_list:
#         for value in item:
#             flattened_list.append(value)
    
#     return flattened_list


# # -------------------- MAIN EXECUTION SECTION --------------------
# if __name__ == "__main__":
#     # 1. Extract title, summary, link, and published
#     all_data = OnlyTitlesAndSummariesWithExtras()
#     print("Extracted Data:", all_data)

#     # 2. Create nested lists of combined data
#     final_list = TitleSummaryLinkPublishedList(all_data)
#     print("Combined Data List:", final_list)

#     # 3. Flatten and print the final result
#     printdepositlist = PrintDeposit(final_list)
#     print("Flattened Deposit List:")
#     print(printdepositlist)

#     # Print to verify length and first item
#     print(f"Total Articles: {len(printdepositlist)}")
#     if len(printdepositlist) > 0:
#         print(f"First Article: {printdepositlist[0]}")
