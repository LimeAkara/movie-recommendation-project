import streamlit as st
import requests
import pandas as pd
from googletrans import Translator
import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import json
import re
import time

# Affichage du logo et du titre
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://i.postimg.cc/4dHWpb2S/image-projet.png" alt="Image Projet" style="width: 60%;">
    </div>
    """, unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: white;'>Bienvenue chez Nostalg'IA</h1>", unsafe_allow_html=True)

st.text("\n")

st.markdown("<h4 style='text-align: center; color: white;'>Si vous n'avez pas encore trouvé votre histoire, nous sommes là pour vous aider !</h4>", unsafe_allow_html=True)

"""---------------------------------------------------------------------------------------------------------------"""

# API URL pour Flask
API_URL_SEARCH = "http://127.0.0.1:5000/search/"
API_URL_RECOMMEND = "http://127.0.0.1:5000/recommend/"

# Configuration de Pandas pour l'affichage
pd.set_option('display.max_columns', None)  # Afficher toutes les colonnes
pd.set_option('display.width', None)  # S'adapter à la largeur totale
pd.set_option('display.max_colwidth', None)  # Ne pas tronquer le contenu des cellules

# Initialisation de `st.session_state` pour stocker les résultats et autres données
if 'results' not in st.session_state:
    st.session_state.results = None
if 'film_renamed' not in st.session_state:
    st.session_state.film_renamed = None
if 'index' not in st.session_state:
    st.session_state.index = None

# Étape 1 : Recherche de films
title = st.text_input("Avez-vous un film que vous avez apprécié durant votre enfance ?", "")

if st.button("Rechercher"):
    if title:
        response = requests.post(API_URL_SEARCH, json={"title": title})
        if response.status_code == 200:
            st.session_state.results = response.json()["results"]
        else:
            st.write("Nous sommes désolé. Aucun film n'a été trouvé avec cette recherche.")

# Si les résultats sont disponibles, afficher les films
if st.session_state.results is not None:
    film_souhaite = pd.DataFrame(st.session_state.results)
    film_souhaite = film_souhaite.fillna("Unknown")

    # Si plusieurs films sont trouvés, les afficher dans un tableau
    if not film_souhaite.empty and len(film_souhaite) > 1:
        film_renamed = film_souhaite.reset_index()
        film_renamed = film_renamed.rename(columns={
            'code': 'ID',
            'originalTitle': 'Film',
            'directors': 'Réalisateur(s)',
            'startYear': 'Année de sortie'
        })
        st.session_state.film_renamed = film_renamed
        st.write("Il y a plusieurs films contenant ce nom, veuillez choisir !")

        film_renamed["Film"] = film_renamed["Film"].apply(lambda x : x.title())

        st.dataframe(film_renamed[['ID', 'Film', 'Réalisateur(s)', 'Année de sortie']], hide_index=True, use_container_width=True)

        # Étape 2 : Sélection du film par ID
        choix = st.text_input("Rentrez l'ID du film qui vous intéresse :")
        
        # Nous utilisons un bouton "Valider" pour confirmer le choix de l'utilisateur
        if st.button("Confirmer"):
            if choix:
                try:
                    # Vérifier si l'ID existe dans le dataframe
                    if int(choix) in film_renamed["ID"].values:
                        film_choisi = film_renamed[film_renamed["ID"] == int(choix)]
                        if not film_choisi.empty:
                            st.session_state.index = film_choisi["ID"].iloc[0]
                        else:
                            st.warning("ID non trouvé.")
                    else:
                        st.warning("Veuillez entrer un ID valide.")
                except ValueError:
                    st.warning("Veuillez entrer un ID valide.")
    
    # Si un seul film est trouvé, afficher directement le film
    elif not film_souhaite.empty and len(film_souhaite) == 1:
        film_renamed = film_souhaite.reset_index()
        film_renamed = film_renamed.rename(columns={
            'code': 'ID',
            'originalTitle': 'Film',
            'directors': 'Réalisateur(s)',
            'startYear': 'Année de sortie'
        })
        st.session_state.index = film_renamed["ID"].iloc[0]
 
    # Si un film a été choisi, récupérer les recommandations
    if st.session_state.index is not None:
        response = requests.post(API_URL_RECOMMEND, json={"index": str(st.session_state.index)})
        if response.status_code == 200:
            recommendations = response.json()["recommendations"]
            film_conseil = pd.DataFrame(recommendations)
            film_conseil = film_conseil.fillna("Unknown")

            # Vérifier si l'index sélectionné existe toujours dans film_renamed
            if st.session_state.index in film_renamed["ID"].values:
                nom_film = film_renamed.loc[film_renamed['ID'] == st.session_state.index, 'Film'].values[0]
                annee = film_renamed.loc[film_renamed['ID'] == st.session_state.index, 'Année de sortie'].values[0]
                
                st.markdown(
    f"<h2 style='text-align: center;'>Vous avez choisi le film {nom_film.title()} de {annee} !</h2>", 
    unsafe_allow_html=True
)


                lien = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"

                film1 =film_renamed[film_renamed["ID"]== st.session_state.index]

                film1["poster_path"] = film1["poster_path"].map(str)

                st.markdown(f'<div style="display: flex; justify-content: center;"><img src="{lien + film1["poster_path"].iloc[0]}" width="400"></div>',unsafe_allow_html=True)

                st.write("\n")

                # Créer un objet Translator
                translator = Translator()

                # Traduire toute la colonne 'overview'
                film1['overview'] = film1['overview'].apply(lambda x: translator.translate(x, src='en', dest='fr').text)

                # Afficher les autres informations du film
                st.write(f"**Genre(s)**: {film1['genres'].iloc[0]}")
                st.write(f"**Réalisateur(s)**: {film1['Réalisateur(s)'].iloc[0]}")
                st.write(f"**Année de sortie**: {film1['Année de sortie'].iloc[0]}")
                st.write(f"**Résumé**:")
                st.write(f"{film1['overview'].iloc[0]}")
    
                """---------------------------------------------------------------------------------------------------------------"""

                st.markdown(
    "<h2 style='text-align: center;'>Nous vous recommandons les films suivants pour raviver vos souvenirs de jeunesse !</h2>", 
    unsafe_allow_html=True
)


                film_conseil = film_conseil.reset_index()
                film_conseil = film_conseil.rename(columns={
                    'code': 'ID',
                    'originalTitle': 'Film',
                    'genres' : 'Genre(s)',
                    'directors': 'Réalisateur(s)',
                    'startYear': 'Année de sortie',
                    'overview' : 'Résumé'
                })
            else:
                st.write("")
        else:
            st.error("Erreur lors de la récupération des recommandations.")

        # Convertir la colonne 'poster_path' en chaîne de caractères (si ce n'est pas déjà le cas)
        film_conseil["poster_path"] = film_conseil["poster_path"].map(str)

        # Construire les liens des posters
        lien = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"
        film_conseil["lien_poster"] = film_conseil["poster_path"].apply(lambda x: lien + x)

        film_conseil = film_conseil.rename(columns={
                    'code': 'ID',
                    'originalTitle': 'Film',
                    'genres' : 'Genre(s)',
                    'directors': 'Réalisateur(s)',
                    'startYear': 'Année de sortie',
                    'overview' : 'Résumé'
                })

        # Liste des liens d'images (les liens de poster des films dans film_choisi_df)
        image_links = film_conseil["lien_poster"].tolist()

        # Créer 5 colonnes dans Streamlit pour afficher les images
        cols = st.columns(5)

        # Boucle pour afficher les images dans chaque colonne
        for i, col in enumerate(cols):
            if i < len(image_links):  # Assurez-vous que l'indice i ne dépasse pas la longueur de la liste
                with col:
                    film_name = film_conseil.iloc[i]["Film"]  # Récupérer le nom du film
                    release_year = film_conseil.iloc[i]["Année de sortie"]  # Récupérer l'année de sortie
                    st.image(image_links[i], caption=f"{film_name.title()} ({release_year})", use_container_width=True)

        st.write("\n")

        # Créer une liste des films pour la sélection dans le selectbox
        film_names = film_conseil["Film"].tolist()

        film_names = [element.title() for element in film_names]

        # Afficher une liste déroulante (selectbox) pour sélectionner un film
        selected_film = st.selectbox("Sélectionnez un film en particulier pour voir les détails", film_names)

        st.markdown(
    f"<h2 style='text-align: center;'>Détails du film : {selected_film.title()}</h2>", 
    unsafe_allow_html=True
)


        st.write("\n")

        # Créer un objet Translator
        translator = Translator()

        # Traduire toute la colonne 'overview'
        film_conseil['Résumé'] = film_conseil['Résumé'].apply(lambda x: translator.translate(x, src='en', dest='fr').text)

        # Récupérer les détails du film sélectionné
        film_details = film_conseil[film_conseil["Film"] == selected_film.lower()].iloc[0]

        # Afficher les détails du film sélectionné

        st.markdown(
        f'<div style="display: flex; justify-content: center;"><img src="{film_details["lien_poster"]}" width="400"></div>',
        unsafe_allow_html=True)

        st.write("\n")

        # Afficher les autres informations du film
        st.write(f"**Genre(s)**: {film_details['Genre(s)']}")
        st.write(f"**Réalisateur(s)**: {film_details['Réalisateur(s)']}")
        st.write(f"**Année de sortie**: {film_details['Année de sortie']}")
        st.write(f"**Résumé**:")
        st.write(f"{film_details['Résumé']}")

        tmdb_link = "https://www.themoviedb.org/movie/"

        titre_tmdb = film_details['Film'].lower().replace(' ', '-')

        if titre_tmdb != 0:
                
            st.write("\n")

            link = f"{tmdb_link}{film_details['tmdb_id']}-{titre_tmdb}"
                
            ua = UserAgent()
            fake_user_agent = ua.random

            page = requests.get(link, headers={'User-Agent': fake_user_agent}) 
            soup = bs(page.content, 'html.parser')
                
            trailer_elements = soup.find_all(class_='no_click play_trailer')

            if trailer_elements:

                st.markdown(
                f"<h2 style='text-align: center;'>Bande Annonce</h2>", 
                unsafe_allow_html=True)

                st.write("\n")
                
                for trailer in trailer_elements:
                # Récupérer la valeur de l'attribut 'data-id'
                    data_id = trailer.get('data-id')
                    yt = f"https://www.youtube.com/watch?v={data_id}"

                    st.video(yt)  

"""---------------------------------------------------------------------------------------------------------------"""