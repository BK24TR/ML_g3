"""
MLModelReturns_4.py

This script will:
  - Import 'MyTheFinalList' from FullRSSList_1_2.py
  - Import the trained model (best_clf_pipeline) + supporting objects (categories, vectorizer, etc.) 
    from MLModelMLC_3.py
  - Use the model to predict categories for the newly fetched RSS articles.
  - Combine the predictions with the final list from 'MyTheFinalList' and possibly produce a
    validated dictionary (validDict).

Students:
 - Complete the pseudo code to transform text, get predictions,
   and merge them with the 'MyTheFinalList'.
"""

# 1) Imports
from FullRSSList_1_2 import MyTheFinalList
from MLModelMLC_3 import categories, x_train, vectorizer, best_clf_pipeline
from RssFeedNewArticle_2 import printdepositlist

import jsonschema
import pickle

def main():
    # 1. Ta text från 'printdepositlist' (title+summary)
    my_text = printdepositlist  # Assuming this is a list of combined title + summary strings
    
    # 2. Filtrera bort tomma strängar
    my_text_no_empty = [t for t in my_text if t.strip() != ""]

    # 3. Transformera text med vectorizer
    my_text_transformed = vectorizer.transform(my_text_no_empty)

    # 4. Prediktera kategorier med modellen
    predictions = best_clf_pipeline.predict_proba(my_text_transformed)

    # 5. Bestäm kategorier baserat på en tröskel
    threshold = 0.3
    results = {}  # dict of text -> list of predicted categories
    for idx, pvector in enumerate(predictions):
        text = my_text_no_empty[idx]
        predicted_categories = [categories[i] for i, prob in enumerate(pvector) if prob >= threshold]
        results[text] = predicted_categories

    # 6. Kombinera 'results' med 'MyTheFinalList'
    combinedList = []
    for idx, item in enumerate(MyTheFinalList):
        title, summary, link, published = item
        text = f"{title} {summary}"
        predicted_topics = results.get(text, [])
        combinedList.append([title, summary, link, published, predicted_topics])

    # 7. Skapa en slutlig lista med dicts
    key_list = ['title', 'summary', 'link', 'published', 'topic']
    finalDict = [dict(zip(key_list, v)) for v in combinedList]

    # 8. Validera slutlig struktur med JSON-schema (valfritt)
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "link": {"type": "string"},
            "published": {"type": "string"},
            "topic": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["title", "summary", "link", "published", "topic"]
    }
    
    valid_list = []
    for item in finalDict:
        try:
            jsonschema.validate(instance=item, schema=schema)
            valid_list.append(item)
        except jsonschema.exceptions.ValidationError as e:
            print(f"Validation error for item {item}: {e}")

    # 9. Exportera den validerade listan 'validDict'
    global validDict # Så att vi kan spara den senare
    validDict = valid_list
    print("Validated dictionary:", validDict)
    #print(f"Total valid items: {len(valid_list)}") #För att validera antalet som gick igenom
    
    # Spara validDict i en pickle-fil
    with open("validDict.pkl", "wb") as file:
      pickle.dump(validDict, file)
  

# Kör scriptet
if __name__ == "__main__":
  main()

  