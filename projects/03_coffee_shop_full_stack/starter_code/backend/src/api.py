import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES


@app.route('/drinks', method=['GET'])
def get_drinks():
    try:
        # Query all drinks
        drinks = Drink.query.all()

        # Return JSON success object (success -> true)
        # and (for statement interating through list of all drinks using drink.short)
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200

    # If fails, throw a 500 (internal error) error code
    except:
        abort(500)


@app.route('/drinks-detail', method=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt_token):
    try:
        # Query all drinks
        drinks = Drink.query.all()

        # Return JSON success object (success -> true)
        # and (for statement iterating through list of all drinks using drink.long)
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200

        # If fails, throw a 500 (internal error) error code
    except:
        abort(500)


@app.route('/drinks', method=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt_token):
    data = request.get_json()

    # If there is no title or recipe, throw abort 404 (not found) error code
    if not data.get('title') or not data.get('recipe'):
        abort(404)

    try:
        # Insert a new drink with the title and recipe input from the JSON request
        new_drink = Drink(title=data.get('title'),
                recipe=json.dumps(data.get('recipe'))
                )
        new_drink.insert()
        
        # Return JSON success object (success -> true)
        # and the new drink using drink.long
        return jsonify({
            'success': True,
            'drinks': new_drink.long()
        }), 200

    # If drink creation fails, throw a 422 (unprocessable) error code
    except Exception:
        abort(422)
        

@app.route('/drinks/<id>', method=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt_token, id):
    data = request.get_json()

    # If there is no title or recipe, throw abort 404 (not found) error code
    if not data.get('title') and not data.get('recipe'):
        abort(404)

    # Query the drink with the matching id number
    update_drink = Drink.query.filter_by(Drink.id=id).one_or_none()

    # If the query returns nothing, throw abort 404 (not found) errow code
    if not update_drink:
        abort(404)

    try:
        # Update the drink details
        update_drink.title = data.get('title')
        update_drink.recipe = data.get('recipe')
        update_drink.update()

        # Return JSON success object (success -> true)
        # and the updated drink using drink.long
        return jsonify({
            'success': True,
            'drinks': update_drink.long()
        }), 200

    # If drink update fails, throw a 422 (unprocessable) error code
    except:
        abort(422)


@app.route('/drinks/<id>', method=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt_token, id):
    try:
        # Query the drink with the matching id number
        remove_drink = Drink.query.filter_by(Drink.id=id).one_or_none()
        
        # If the query returns nothing, throw abort 404 (not found) errow code
        if not remove_drink:
            abort(404)

        # Delete the drink
        remove_drink.delete()

        # Return JSON success object (success -> true)
        # and the deleted drink's id number
        return jsonify({
            'success': True,
            'delete': id
        }), 200

    # If drink update fails, throw a 422 (unprocessable) error code
    except:
        abort(422)


# Error Handling

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500

@app.errorhandler(AuthError)
def handle_auth_error(exception):
    return return jsonify({
        "success": False,
        "error": 401,
        'message': exception.error
    }), 401
