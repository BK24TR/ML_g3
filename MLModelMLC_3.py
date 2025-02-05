"""
MLModelMLC_3.py

This script trains a multi-label text classification model using data from Book1.csv.
It:
  - Loads and preprocesses the data
  - Trains a MultinomialNB-based OneVsRest model with GridSearchCV
  - Prints out the best model and accuracy
  - Exposes certain variables for import into other scripts:
       categories, x_train, vectorizer, best_clf_pipeline
"""

import re
import sys
import warnings
import pickle
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# Suppress warnings for clarity
if not sys.warnoptions:
    warnings.simplefilter("ignore")

# Function to preprocess text
def preprocess_text(data_raw):
    data_raw['Heading'] = (
        data_raw['Heading']
        .str.lower()
        .str.replace(r'[^\w\s]', '', regex=True)
        .str.replace(r'\d+', '', regex=True)
        .str.replace(r'<.*?>', '', regex=True)
    )

    nltk.download('stopwords')
    stop_words = set(stopwords.words('swedish'))

    def removeStopWords(sentence):
        return " ".join([word for word in nltk.word_tokenize(sentence) if word not in stop_words])

    data_raw['Heading'] = data_raw['Heading'].apply(removeStopWords)

    stemmer = SnowballStemmer("swedish")

    def stemming(sentence):
        stemSentence = ""
        for word in sentence.split():
            stem = stemmer.stem(word)
            stemSentence += stem
            stemSentence += " "
        return stemSentence.strip()

    # Uncomment if stemming is needed
    # data_raw['Heading'] = data_raw['Heading'].apply(stemming)

    return data_raw

# 1) Load the data
data_path = "Book1.csv"  # Adjust path if needed
data_raw = pd.read_csv(data_path)

# 2) Shuffle the data
data_raw = data_raw.sample(frac=1)

# 3) Preprocessing
categories = list(data_raw.columns.values)
categories = categories[2:]  # Usually, 'Id' and 'Heading' are the first two columns
data_raw = preprocess_text(data_raw)

# 4) Split the data
train, test = train_test_split(data_raw, random_state=42, test_size=0.30, shuffle=True)
train_text = train['Heading']
test_text = test['Heading']

# 5) Vectorize
vectorizer = TfidfVectorizer(strip_accents='unicode', analyzer='word', ngram_range=(1, 3), norm='l2')
vectorizer.fit(train_text)

x_train = vectorizer.transform(train_text)
y_train = train.drop(labels=['Id', 'Heading'], axis=1)

x_test = vectorizer.transform(test_text)
y_test = test.drop(labels=['Id', 'Heading'], axis=1)

# 6) Setup ML pipeline
MultinomialNB_pipeline = Pipeline([
    ('clf', OneVsRestClassifier(MultinomialNB())),
])

# 7) Hyperparameter Tuning
param_grid = {
    'clf__estimator__alpha': [0.20, 0.21, 0.22],
    'clf__estimator__fit_prior': [True, False]
}

grid = GridSearchCV(MultinomialNB_pipeline, param_grid, cv=5, scoring='accuracy')
grid.fit(x_train, y_train)

print("Best score: ", grid.best_score_)
print("Best params: ", grid.best_params_)
print("Best estimator: ", grid.best_estimator_)

best_clf_pipeline = grid.best_estimator_
best_clf_pipeline.fit(x_train, y_train)

# 8) Predict on test data
y_pred_proba = best_clf_pipeline.predict_proba(x_test)
threshold = 0.3  # Adjust threshold if needed
y_pred = (y_pred_proba >= threshold).astype(int)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# # Save objects to a file for later use
# with open('model_objects.pkl', 'wb') as file:
#     pickle.dump({
#         'categories': categories,
#         'x_train': x_train,
#         'vectorizer': vectorizer,
#         'best_clf_pipeline': best_clf_pipeline
#     }, file)

# print("Model objects have been saved to 'model_objects.pkl'.")

# Expose objects for direct import
categories = categories
x_train = x_train
vectorizer = vectorizer
best_clf_pipeline = best_clf_pipeline
