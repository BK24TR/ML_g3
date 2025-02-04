import pandas as pd
# Importerar funktion för att hämta en df
from RSS_Articles import fetch_posts 
# Importerar modell, kategorier, vektoriserare och träningsdata
from BestModel import best_clf, categories, vectorizer, x_train 

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
y_pred_proba = best_clf.predict_proba(X_rss)
threshold = 0.3
y_pred_adjusted = (y_pred_proba >= threshold).astype(int) 
# Omvandla till DataFrame med rätt kolumnnamn
y_pred_df = pd.DataFrame(y_pred_adjusted, columns=categories)

# Lägg till prediktionerna i final_RSS
final_RSS[categories] = y_pred_df

# Kontrollera resultatet
print(final_RSS[categories].head(10))