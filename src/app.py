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
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
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

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "example_password"  
jwt = JWTManager(app)

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
def get_all_planets():
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
def get_one_planet(planet_id):
    try:
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify({"error": "Character not found"}), 404
        
        return jsonify(planet.serialize()), 200

    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()

        email = data.get('email')
        password = str(data.get('password'))  
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        is_active = data.get('is_active', True)  

        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"msg": "User already exists"}), 400

        new_user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"msg": "User created successfully"}), 201

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = str(data.get('password'))

        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"msg": "User not found"}), 404

        if user.password != password:
            return jsonify({"msg": "Incorrect password"}), 401

        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

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
@app.route("/users/favorites", methods=["GET"])
@jwt_required()  
def get_user_favorites():
    try:
        user_id = get_jwt_identity()
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
    
@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "Missing user_id in request body"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        planet = Planet.query.get(planet_id)
        if not planet:
            return jsonify({"error": "Planet not found"}), 404

        new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
        db.session.add(new_favorite)
        db.session.commit()

        return jsonify({"message": "Favorite planet added"}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_character(people_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "Missing user_id in request body"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        character = Character.query.get(people_id)
        if not character:
            return jsonify({"error": "Character not found"}), 404

        new_favorite = Favorite(user_id=user_id, character_id=people_id)
        db.session.add(new_favorite)
        db.session.commit()

        return jsonify({"message": "Favorite character added"}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "Missing user_id in request body"}), 400

        favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

        if not favorite:
            return jsonify({"error": "Favorite planet not found"}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({"message": "Favorite planet deleted successfully"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    
@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_character(people_id):
    try:
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "Missing user_id in request body"}), 400

        favorite = Favorite.query.filter_by(user_id=user_id, character_id=people_id).first()

        if not favorite:
            return jsonify({"error": "Favorite character not found"}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({"message": "Favorite character deleted successfully"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
