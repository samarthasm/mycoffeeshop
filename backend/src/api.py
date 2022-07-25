import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
# To run Server, executing from backend directory:
# set FLASK_APP=api.py
# set FLASK_ENV=development
# python -m flask run
setup_db(app)
CORS(app)

#----------------------------------------------------------------------------#
# TODO_complete
# Uncommentefd the following line to initialize the database
#----------------------------------------------------------------------------#

db_drop_and_create_all()

#----------------------------------------------------------------------------#
# The following custom method queries the list of drinks with a string 
# input (long/short recipe description) and outputs the list of drinks.
# If no drinks are found, it aborts with 404 error.
#----------------------------------------------------------------------------#

def get_all_drinks(recipe_format):

    # Get all drinks in database
    all = Drink.query.order_by(Drink.id).all()
    # Format with different recipe detail level
    if recipe_format.lower() == 'short':
        all_drinks_formatted = [drink.short() for drink in all]
    elif recipe_format.lower() == 'long':
        all_drinks_formatted = [drink.long() for drink in all]
    else:
        return abort(500, {'message': 'bad formatted function call. recipe_format needs to be "short" or "long".'})

    if len(all_drinks_formatted) == 0:
        abort(404, {'message': 'no drinks found in database.'})
    
    # Return formatted list of drinks
    return all_drinks_formatted

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


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

#----------------------------------------------------------------------------#
# Error Handlers
# TODO_complete
# Implementing error handlers using the @app.errorhandler(error) decorator
#----------------------------------------------------------------------------#

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

#----------------------------------------------------------------------------#
# TODO_complete 
# Implementing error handler for 404
#----------------------------------------------------------------------------#

@app.errorhandler(404)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

#----------------------------------------------------------------------------#
# TODO_complete 
# Implementing error handler for AuthError
#----------------------------------------------------------------------------#

@app.errorhandler(AuthError)
def authentification_failed(AuthError): 
    return jsonify({
                    "success": False, 
                    "error": AuthError.status_code,
                    "message": "authentification fails"
                    }), 401