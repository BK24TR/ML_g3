import subprocess

# import pickle
# import jsonschema
# from datetime import datetime
# import pandas as pd
# import feedparser
# import nltk

# import RssArticles_1
# import FullRSSList_1_2
# import RssFeedNewArticle_2
# import MLModelMLC_3
# import MLModelReturns_4
# import DbTransfer_5

scripts = ["RssArticles_1.py", "FullRSSList_1_2.py"
           , "RssFeedNewArticle_2.py", "MLModelMLC_3.py"
           , "MLModelReturns_4.py", "DbTransfer_5.py"]

for script in scripts:
    subprocess.run(["python", script])  # Kör varje script i ordning

print("Nu körs din mamma..")