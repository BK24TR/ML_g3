"""
MLModelMLC_3.py

This script trains a multi-label text classification model using data from Book1.csv.
It:
  - Loads and preprocesses the data
  - Trains a LogisticRegression-based OneVsRest model with GridSearchCV
  - Prints out the best model and accuracy
  - Exposes certain variables for import into other scripts:
       categories, x_train, vectorizer, best_clf_pipeline

Important for the assignment:
 - Students can attempt to modify hyperparameters or the threshold value to see if it
   improves accuracy or better suits the data.
 - Make sure that once the model is finalized, you "export" the key objects so that
   MLModelReturns_4 can import them.

"""

import sys
import warnings
import nltk
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB

# If needed for your environment:
nltk.data.path.append('/usr/local/share/nltk_data')

# Suppress warnings for clarity
if not sys.warnoptions:
    warnings.simplefilter("ignore")

# 1) Load the data
data_path = r"C:\workspace\ML\ML-course\inlämning2\Book1.csv"  # Student: adjust if your CSV is somewhere else
data_raw = pd.read_csv(data_path)

# 2) Shuffle the data
data_raw = data_raw.sample(frac=1)

# 3) Preprocessing
categories = list(data_raw.columns.values)
categories = categories[2:]  # Usually, 'Id' and 'Heading' are the first two columns

data_raw['Heading'] = (
    data_raw['Heading']
    .str.lower()
    .str.replace(r'[^\w\s]', '', regex=True)
    .str.replace(r'\d+', '', regex=True)
    .str.replace(r'<.*?>', '', regex=True)
)

# nltk.download('stopwords')
stop_words = set(stopwords.words('swedish'))

def removeStopWords(sentence):
    return " ".join(
        [word for word in nltk.word_tokenize(sentence)
         if word not in stop_words]
    )

data_raw['Heading'] = data_raw['Heading'].apply(removeStopWords)

stemmer = SnowballStemmer("swedish")

def stemming(sentence):
    stemSentence = ""
    for word in sentence.split():
        stem = stemmer.stem(word)
        stemSentence += stem
        stemSentence += " "
    return stemSentence.strip()

# (Optional) If you want to apply stemming, uncomment the next line:
# data_raw['Heading'] = data_raw['Heading'].apply(stemming)

# 4) Split the data
train, test = train_test_split(data_raw, random_state=42, test_size=0.30, shuffle=True)
train_text = train['Heading']
test_text = test['Heading']

# 5) Vectorize
vectorizer = TfidfVectorizer(strip_accents='unicode', 
                             analyzer='word', 
                             ngram_range=(1,3),
                             norm='l2')
vectorizer.fit(train_text)

x_train = vectorizer.transform(train_text)
y_train = train.drop(labels = ['Id','Heading'], axis=1)

x_test = vectorizer.transform(test_text)
y_test = test.drop(labels = ['Id','Heading'], axis=1)

'''WITH PIPELINE'''
# 6) Setup ML pipeline
# NB_pipeline = Pipeline([
#     ('clf', OneVsRestClassifier(MultinomialNB())),
# ])

# # 7) Hyperparameter Tuning
# param_grid = {
#     'clf__estimator__alpha': [0.01, 0.1, 0.5, 1.0],  # Korrekt namn för parametern
#     'clf__estimator__fit_prior': [True, False]
# }

# grid = GridSearchCV(
#     NB_pipeline, 
#     param_grid, 
#     cv=5, 
#     scoring='accuracy', 
#     n_jobs=-1
#     )

# grid.fit(x_train, y_train)  # Använd vektoriserad text, inte råtext!


# # Spara den bästa modellen
# best_clf_pipeline = grid.best_estimator_

# # Träna modellen
# best_clf_pipeline.fit(x_train, y_train)

# # Gör prediktioner
# y_pred = best_clf_pipeline.predict(x_test)  # Bytt från predict_proba()

# # Beräkna noggrannhet
# accuracy = accuracy_score(y_test, y_pred)
# print("Accuracy:", accuracy)
# print("Best params:", grid.best_params_)
# print("Best score:", grid.best_score_)


'''WITHOUT PIPELINE'''

clf = OneVsRestClassifier(MultinomialNB())
# Definiera parametergrid för MultinomialNB inom OneVsRestClassifier
param_grid = {
    'estimator__alpha': [0.01, 0.1, 0.5, 1.0],  # Smoothing-parameter
    'estimator__fit_prior': [True, False]  # Testa om prior sannolikheter hjälper
}


# Skapa GridSearchCV för att hitta bästa parametrarna
grid_search = GridSearchCV(
    estimator=clf,
    param_grid=param_grid,
    cv=5,  # Cross-validation folds
    scoring='f1_weighted',  # Optimerar f1-score
    n_jobs=-1  # Kör parallellt på flera kärnor
)

# Kör GridSearchCV på träningsdatan
grid_search.fit(x_train, y_train)

# Visa de bästa parametrarna och poängen
# print("Best params:", grid_search.best_params_)
# print("Best score:", grid_search.best_score_)

# Träna om modellen med de bästa parametrarna
best_clf = grid_search.best_estimator_
best_clf.fit(x_train, y_train)



# Make sure to "expose" these objects for import:
categories = categories
x_train = x_train
vectorizer = vectorizer
# best_clf_pipeline = best_clf_pipeline
best_clf = best_clf
