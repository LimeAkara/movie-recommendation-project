import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.pipeline import Pipeline
import re
import string
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
from sklearn.neighbors import NearestNeighbors
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
lemmatizer = WordNetLemmatizer()
from sklearn.preprocessing import OneHotEncoder
import nltk
nltk.download('popular')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('vader_lexicon')
nltk.download('punkt_tab')
import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import re

dfML = pd.read_csv(r'C:\Users\aozak\data formation\projet 2\projet streamlit\dfML1.csv', sep=",")
dfML2 = dfML[['code', 'originalTitle', 'title', 'genres','overview', 'poster_path',
       'directors', 'startYear', 'averageRating', 'numVotes', 'Action',
       'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama',
       'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery',
       'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western','Cluster']] 
def preprocess_text(text):
    # Convertir en minuscules
    text = text.lower()
    # Enlever les caractères inutiles (ponctuation, chiffres, etc.)
    text = re.sub(r'[\W_]+', ' ', text)  # Enlève tout sauf les mots et les espaces
    # Tokenization
    tokens = word_tokenize(text)
    # Lemmatisation
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(lemmatized_tokens)  # Retourner le texte lemmatisé sous forme de chaîne

dfML2['overview']=dfML2['overview'].apply(lambda x : preprocess_text(x))
dfML2['directors']=dfML2['directors'].apply(lambda x : preprocess_text(x))

# Créer un transformateur personnalisé pour appliquer un poids
class WeightedOneHotEncoder(BaseEstimator, TransformerMixin):
    def __init__(self, weight=1.0):
        self.weight = weight
        self.encoder = OneHotEncoder()

    def fit(self, X, y=None):
        self.encoder.fit(X, y)
        return self

    def transform(self, X):
        # Appliquer l'encodage et multiplier par le poids
        return self.encoder.transform(X).toarray() * self.weight

class WeightedStandardScaler(BaseEstimator, TransformerMixin):
    def __init__(self, weight=1.0):
        self.weight = weight
        self.scaler = StandardScaler()

    def fit(self, X, y=None):
        self.scaler.fit(X, y)
        return self

    def transform(self, X):
        # Appliquer le scaling et multiplier par le poids
        return self.scaler.transform(X) * self.weight
    


clust_features = ['Cluster','averageRating', 'numVotes']
clust_transformer = Pipeline(steps=[
    ('scaler', WeightedStandardScaler(weight=5))]) 

date_features = ['startYear']
date_transformer = Pipeline(steps=[
    ('scaler', WeightedStandardScaler(weight=50))]) 
over_features = ['overview']
over_transformer = Pipeline(steps=[('encoder', WeightedOneHotEncoder(weight=50))])
dir_features = ['directors']
dir_transformer = Pipeline(steps=[('encoder', WeightedOneHotEncoder(weight=30))])
genre_features = ['Action',
       'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama',
       'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery',
       'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western']
genre_transformer = Pipeline(steps=[('encoder', WeightedStandardScaler(weight=10))])

# Combiner les transformateurs dans un ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', clust_transformer, clust_features),
        ('date', date_transformer, date_features),
        ('over', over_transformer, over_features),
        ('genre',genre_transformer,genre_features),
        ('dir', dir_transformer,dir_features)
    ])

#On crée notre modèle

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('knn', NearestNeighbors(n_neighbors=6, metric= 'euclidean'))])

X = dfML2[['startYear', 'averageRating', 'numVotes','Cluster','overview','Action',
       'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama',
       'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery',
       'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western','directors']]

feat = ['startYear','Cluster','overview','Action','averageRating', 'numVotes',
       'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama',
       'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery',
       'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western','directors']

pipeline.fit(X)

def nom_film(film):
    # Filtrer les lignes où le titre du film correspond
    film = film.strip().lower()
    df_filtre = dfML[dfML['title'].str.contains(film, case=False, na=False) | dfML['originalTitle'].str.contains(film, case=False, na=False)]
  
    if not df_filtre.empty:
        # Si une seule ligne correspond, retourner directement cette ligne
        return df_filtre
    else:
        # Aucun film trouvé
        print("Aucun film trouvé.")
        return None


def suggestion(id):
    
    id = int(id)
    
    film= dfML2[dfML2["code"] == id]                         # normalisation des données du film 
    film1= pipeline.named_steps['preprocessor'].transform(film[feat])

    distances,indices = pipeline.named_steps['knn'].kneighbors(film1)             # recherche voisin 

    df_suggest = dfML.iloc[indices[0]]
    
    df_suggest = df_suggest.iloc[1:]
    
    return df_suggest
