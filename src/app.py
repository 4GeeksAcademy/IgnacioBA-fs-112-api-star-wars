"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models import db, User, Planet, Character, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Get de todos los characters/people
@app.route("/people", methods=["GET"])
def get_all_people():
    try:
        characters = Character.query.all()
        if not characters:
            return jsonify({"error": "No characters found"}), 404

        result = [character.serialize() for character in characters]
        return jsonify(result), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
# Get de un character/people
@app.route("/people/<int:people_id>", methods=["GET"])
def get_one_person(people_id):
    try:
        character = Character.query.get(people_id)
        if character is None:
            return jsonify({"error": "Character not found"}), 404
        
        return jsonify(character.serialize()), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
# Get de todos los planets
@app.route("/planets", methods=["GET"])
def get_all_people():
    try:
        planets = Planet.query.all()
        if not planets:
            return jsonify({"error": "No characters found"}), 404

        result = [planet.serialize() for planet in planets]
        return jsonify(result), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
# Get de un planet
@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_one_person(planet_id):
    try:
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify({"error": "Character not found"}), 404
        
        return jsonify(planet.serialize()), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# Get de todos los users   
@app.route("/users", methods=["GET"])
def get_all_users():
    try:
        users = User.query.all()
        if not users:
            return jsonify({"error": "No characters found"}), 404

        result = [user.serialize() for user in users]
        return jsonify(result), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# Get de los favoritos de un user
@app.route("/users/<int:user_id>/favorites", methods=["GET"])
def get_user_favorites(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        favorites = Favorite.query.filter_by(user_id=user_id).all()
        if not favorites:
            return jsonify({"message": "No favorites found for this user."}), 404

        result = []
        for fav in favorites:
            if fav.character_id:
                result.append({
                    "type": "character",
                    "id": fav.character_id,
                    "name": fav.character.name
                })
            elif fav.planet_id:
                result.append({
                    "type": "planet",
                    "id": fav.planet_id,
                    "name": fav.planet.name
                })

        return jsonify(result), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
