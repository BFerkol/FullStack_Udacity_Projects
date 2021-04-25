import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = QUESTIONS_PER_PAGE * (page - 1)
    end = QUESTIONS_PER_PAGE + start

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = Category.query.order_by(Category.type).all()

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''
  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories = Category.query.order_by(Category.type).all()

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': {category.id: category.type for category in categories},
      'current_category': None})

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question_by_id(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()
    if not question:
      abort(404)
    
    try:
      question.delete()
      return jsonify({
        'success' : True,
        'deleted' : question_id
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  '''
  @app.route('/questions', methods=['POST'])
  def create_or_search_questions():
    body = request.get_json()

    # If request does not contain valid JSON, raise 400.
    if not body:
      abort(400)
    search_term = body.get('searchTerm', None)
    if search_term:
      # If json body contains a search term, execute question search
      questions = Question.query.filter(Question.question.contains(search_term)).all()

      # If no question could be found, return 404
      if not questions:
        abort(404)
    
      # If questions have been found, format result and return succesfull response
      questions_found = [question.format() for question in questions]
      selections = Question.query.order_by(Question.id).all() # needed for total_questions
      

      return jsonify({
        'success': True,
        'questions': questions_found,
        'total_questions': len(selections),
        'current_category' : None
      })

    # Get field informations from request body
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    # Make sure that all requiered fields are given.
    # Otherwise, respond with error message that describes what is missing
    if not new_question:
      abort(400, {'message': 'Question is a mandatory field'})

    if not new_answer:
      abort(400, {'message': 'Answer is a mandatory field'})

    if not new_category:
      abort(400, {'message': 'Category is a mandatory field'})

    if not new_difficulty:
      abort(400, {'message': 'Difficulty is a mandatory field'})

    try:
      # Try to insert a new question. If anything went wrong, raise 422 "unprocessable"
      question = Question(
        question = new_question, 
        answer = new_answer, 
        category= new_category,
        difficulty = new_difficulty
        )
      question.insert()

      # After succesfully insertion, get all paginated questions 
      selections = Question.query.order_by(Question.id).all()
      questions_paginated = paginate_questions(request, selections)

      # Return succesfull response
      return jsonify({
        'success': True,
        'created': question.id,
        'questions': questions_paginated,
        'total_questions': len(selections)
      })

    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    if search_term:
      search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

      return jsonify({
        'success': True,
        'questions': [question.format() for question in search_results],
        'total_questions': len(search_results),
        'current_category': None})
    abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_from_categories(category_id):
    # Query with category id for every question
    if category_id!=0:
      selection = (Question.query
      .filter(Question.category == category_id)
      .order_by(Question.id)
      .all())
    else:
      selection = (Question.query.order_by(Question.id).all())

    # If no questions in the category
    if not selection:
      abort(400)

    # Paginate
    questions_paginated = paginate_questions(request, selection)

    # If paginated questions is empty it means the page selected does not contain any questions
    if not questions_paginated:
      abort(404, {'message': 'No questions in selected page.'})

    # Return succesfull response
    return jsonify({
      'success': True,
      'questions': questions_paginated,
      'total_questions': len(selection),
      'current_category' : category_id
      })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()

    if not body:
      # If no JSON Body was given, raise error.
      abort(400, {'message': 'Please provide a JSON body with previous question Ids and optional category.'})
    
    # Get paramters from JSON Body.
    previous_questions = body.get('previous_questions', None)
    current_category = body.get('quiz_category', None)

    if not previous_questions:
      if current_category and current_category['id']!=0:
        # if no list with previous questions is given, but a category , just gut any question from this category.
        questions_raw = (Question.query
          .filter(Question.category == str(current_category['id']))
          .all())
      else:
        # if no list with previous questions is given and also no category , just gut any question.
        questions_raw = (Question.query.all())    
    else:
      if current_category and current_category['id']!=0:
      # if a list with previous questions is given and also a category, query for questions which are not contained in previous question and are in given category
        questions_raw = (Question.query
          .filter(Question.category == str(current_category['id']))
          .filter(Question.id.notin_(previous_questions))
          .all())
      else:
        # # if a list with previous questions is given but no category, query for questions which are not contained in previous question.
        questions_raw = (Question.query
          .filter(Question.id.notin_(previous_questions))
          .all())
    
    # Format questions & get a random question
    questions_formatted = [question.format() for question in questions_raw]
    random_question = questions_formatted[random.randint(0, len(questions_formatted)-1)]
    
    return jsonify({
        'success': True,
        'question': random_question
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": getErrorMessage(error, "bad request")
      }), 400

  @app.errorhandler(404)
  def ressource_not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": getErrorMessage(error, "resource not found")
      }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": getErrorMessage(error, "unprocessable")
      }), 422
  
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "internal server error"
      }), 500

  def getErrorMessage(error, default_text):
    try:
      return error.description["message"]
    except TypeError:
      return default_text
  
  return app

    