import pandas as pd
# Importerar funktion för att hämta en df
from RSS_Articles import fetch_posts 
# Importerar modell, kategorier, vektoriserare och träningsdata
from BestModel import best_clf_pipeline, categories, vectorizer, x_train 
import json
from jsonschema import validate, ValidationError

# Hämta RSS-poster i en dataframe
final_RSS = fetch_posts()
# Printa top fem raden på dataframen
# print(final_RSS.head())

# Vektorisera Heading
X_rss = vectorizer.transform(final_RSS['Heading'])

# Lägg till kategorikolumner och fyll med 0
for category in categories:
    final_RSS[category] = 0  # Initialt sätt alla till 0

# Prediktera kategorier för RSS-artiklar
y_pred_proba = best_clf_pipeline.predict_proba(X_rss)
threshold = 0.3
y_pred_adjusted = (y_pred_proba >= threshold).astype(int) 
# Omvandla till DataFrame med rätt kolumnnamn
y_pred_df = pd.DataFrame(y_pred_adjusted, columns=categories)

# Lägg till prediktionerna i final_RSS
final_RSS[categories] = y_pred_df

# Kontrollera resultatet
# print(final_RSS[categories].head(10))
# print(final_RSS.head())

# räkna antalet rader där inga katogorier är predikterade
# no_category = final_RSS[categories].sum(axis=1) == 0
# print(f"Antal rader utan kategori: {no_category.sum()}")
# # räkna fyllda rader
# filled_rows = final_RSS.shape[0] - no_category.sum()
# print(f"Antal rader med kategori: {filled_rows}")

#Skapa en final strukturerad lista (MyTheFinalList)


MyTheFinalList = final_RSS.to_dict(orient="records")

#Definiera JSON-schema för validering
rss_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "Heading": {"type": "string"},
            "Link": {"type": "string"},
            "Date": {"type": "string"},
            **{category: {"type": "integer"} for category in categories}  # Dynamiska kategorier
        },
        "required": ["Heading", "Link", "Date"]  # Obligatoriska fält
    }
}

#Validera JSON-strukturen
try:
    validate(instance=MyTheFinalList, schema=rss_schema)
    print("✅ JSON-data är validerad och korrekt!")
except ValidationError as e:
    print("❌ JSON-data har ett fel:", e)

#Konvertera till JSON och spara
validDict = json.dumps(MyTheFinalList, ensure_ascii=False, indent=4)

with open(r"C:\workspace\ML\ML-course\Gruppuppgift\Final\rss_classified.json", "w", encoding="utf-8") as f:
    f.write(validDict)

#Returnera JSON för vidare användning
print("✅ JSON-fil sparad som 'rss_classified.json'")


#Kontrollera resultatet
print(final_RSS[categories].head(20))