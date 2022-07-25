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

#----------------------------------------------------------------------------#
# The endpoints configuration
#----------------------------------------------------------------------------#

# ---------------------------------------------------------------------------#
# TODO_complete
# This is an endpoint to get all drinks
# ---------------------------------------------------------------------------#

@app.route('/drinks' , methods=['GET'])
def drink():
    return jsonify({
    'success': True,
    'drinks': get_all_drinks('short')
    }), 200

# ---------------------------------------------------------------------------#
# TODO_complete
# This is an endpoint to get drinks details
# ---------------------------------------------------------------------------#

@app.route('/drinks-detail',  methods=['GET'])
@requires_auth('get:drinks-detail')
def drinkdetail(payload):
    return jsonify({
    'success': True,
    'drinks': get_all_drinks('long')
    }), 200

# ---------------------------------------------------------------------------#
# TODO_complete
# This is an endpoint to post drinks
# ---------------------------------------------------------------------------#

@app.route('/drinks',  methods=['POST'])
@requires_auth('post:drinks')
def create(payload):
    
    bdy = request.get_json()
    new = Drink(title = bdy['title'], recipe = """{}""".format(bdy['recipe']))
    
    new.insert()
    new.recipe = bdy['recipe']
    return jsonify({
    'success': True,
    'drinks': Drink.long(new)
    })

# ---------------------------------------------------------------------------#
# TODO_complete
# This is an endpoint to update/edit existing drinks
# ---------------------------------------------------------------------------#
    
@app.route('/drinks/<int:drink_id>',  methods=['PATCH'])
@requires_auth('patch:drinks')
def update(payload, drink_id):
    
    # Get body from request
    bdy = request.get_json()

    if not bdy:
      abort(400, {'message': 'request does not contain a valid JSON body.'})
    
    # Find drink which should be updated by id
    update = Drink.query.filter(Drink.id == drink_id).one_or_none()

    # Check if and which fields should be updated
    title = bdy.get('title', None)
    recipe = bdy.get('recipe', None)
    
    # Depending on which fields are available, make apropiate updates
    if title:
        update.title = bdy['title']
    
    if recipe:
        update.recipe = """{}""".format(bdy['recipe'])
    
    update.update()

    return jsonify({
    'success': True,
    'drinks': [Drink.long(update)]
    })

# ---------------------------------------------------------------------------#
# TODO_complete
# This is an endpoint to delete existing drinks
# ---------------------------------------------------------------------------#

@app.route('/drinks/<int:drink_id>',  methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    if not drink_id:
        abort(422, {'message': 'Please provide valid drink id'})

    # Get drink with id
    delete = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if not delete:
        abort(404, {'message': 'Drink with id {} not found in database.'.format(drink_id)})
     
    delete.delete()
    
    return jsonify({
    'success': True,
    'delete': drink_id
    })

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