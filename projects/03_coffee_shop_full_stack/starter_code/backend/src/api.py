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
        })
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
        })
        # If fails, throw a 500 (internal error) error code
    except:
        abort(500)


@app.route('/drinks', method=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt_token):
    data = request.get_json()

    try:
        # Insert a new drink with the title and recipe input from the JSON request
        new_drink = Drink(title=data.get('title'),
                recipe=json.dumps(data.get('recipe'))
                )
        new_drink.insert()
        
        # Return JSON success object (success -> true)
        # and the new drink using drink.long representation
        return jsonify({
            'success': True,
            'drinks': new_drink.long()
        })

    # If drink creation fails, throw a 422 (unprocessable) error code
    except Exception:
        abort(422)
        

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', method=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt_token, id):
    data = request.get_json()

    # If there is no title or recipe, throw abort 404 (not found) error code
    if not data.get('title') and not data.get('recipe'):
        abort(404)

    try:
        # Query the drink with the match id number
        update_drink = Drink.query.filter_by(Drink.id=id).one_or_none()

        # If the query returns nothing, throw abort 404 (not found) errow code
        if not update_drink:
            abort(404)

        # Update the drink details and update to the database
        update_drink.title = data.get('title')
        update_drink.recipe = data.get('recipe')
        update_drink.update()

        return jsonify({
            'success': True
            'drinks': update_drink.long()
        })

    #  If drink update fails, throw a 422 (unprocessable) error code
    except:
        abort(422)




        

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', method=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt_token, id)


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
        "message": "unprocessable"
    }), 500


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
