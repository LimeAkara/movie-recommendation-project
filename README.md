# Concept du projet

Un projet scolaire qui vise à sortir une application de recommandation de film à partir des données sur le cinéma qu'on a sur la main. A partir d'un nom de film, l'application conseille 5 films sortis vers la même époque (l'algorithme de recommandation met beaucoup de poids sur l'année de sortie).

# Les étapes du projet

- Faire de l'EDA (Exploratory Data Analysis, Analyse exploratoire des données en français) sur la base de données public de IMDB et TMDB. Analyser, nettoyer, organiser les données et en retenir que ce qui nous intérsse
- Tester des modèles de Machine Learning et identifier les caractéristiques importants à utiliser sur les données propres et nettoyées. Quelques web scraping léger pour combler les données manquantes qu'on a besoin (notamment les synopsis manquants).
- Création d'une API (avec API flask ici) pour exploiter efficacement le modèle de recommandation.
- Création d'un front de website avec Streamlit pour afficher le projet.

# Les détails des fichiers de ce repository

- Un fichier .py contenant les codes du modèle de recommendation
- Un fichier .py contenant la création de l'API flask
- Un fichier .py contenant le front du Streamlit + une petite partie de web scraping pour afficher les bandes-annonces des films
- A venir : Peut-être un fichier .ipynb de l'EDA complet réalisé pour le projet
