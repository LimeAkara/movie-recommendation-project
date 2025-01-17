from flask import Flask, request, jsonify
from pydantic import BaseModel
from flask_restful import Api, Resource
import logging

# Importer les fonctions existantes depuis votre module
from recommendation import nom_film, suggestion

# Initialisation de l'application Flask
app = Flask(__name__)
api = Api(app)

# Configurer le logging pour l'application
logging.basicConfig(level=logging.DEBUG)

# Modèle Pydantic pour la recherche de films
class MovieSearchRequest(BaseModel):
    title: str

# Modèle Pydantic pour la recommandation de films
class MovieRecommendRequest(BaseModel):
    index: int

class MovieSearchResource(Resource):
    def post(self):
        """
        Recherche de films par titre.
        """
        # Charger les données JSON envoyées
        data = request.get_json()
        try:
            # Validation des données d'entrée avec Pydantic
            movie_request = MovieSearchRequest(**data)
            title = movie_request.title

            # Appeler la fonction importée nom_film pour obtenir les résultats
            results = nom_film(title)
            if results.empty:
                return {'detail': 'Aucun film trouvé.'}, 404
            
            # Retourner les films possibles
            return {'results': results.to_dict(orient='records')}, 200
        except Exception as e:
            logging.error(f"Erreur de recherche : {e}")
            return {'detail': 'Erreur de traitement.'}, 500

class MovieRecommendResource(Resource):
    def post(self):
        """
        Recommande des films basés sur l'index d'un film choisi.
        """
        data = request.get_json()
        try:
            # Validation des données d'entrée avec Pydantic
            movie_request = MovieRecommendRequest(**data)
            index = movie_request.index

            # Appeler la fonction importée suggestion pour obtenir les recommandations
            recommendations = suggestion(index)
            return {'recommendations': recommendations.to_dict(orient='records')}, 200
        except IndexError:
            logging.error(f"Index invalide : {data}")
            return {'detail': 'Index de film invalide.'}, 400
        except Exception as e:
            logging.error(f"Erreur de recommandation : {e}")
            return {'detail': 'Erreur de traitement.'}, 500

# Ajout des ressources aux routes Flask
api.add_resource(MovieSearchResource, '/search/')
api.add_resource(MovieRecommendResource, '/recommend/')

if __name__ == '__main__':
    # Lancer l'application Flask
    app.run(debug=True)  
  

