import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

'''Paginate function'''
def paginate_questions(request, selection):
	page = request.args.get('page', 1, type=int)
	start = QUESTIONS_PER_PAGE * (page - 1)
	end = QUESTIONS_PER_PAGE + start

	questions = [question.format() for question in selection]
	current_questions = questions[start:end]

	return current_questions


def create_app(test_config=None):
# create and configure the app
	app = Flask(__name__)
	setup_db(app)
  
	'''
	Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
	'''
	CORS(app, resources={"/": {"origins": "*"}})

	'''
	Use the after_request decorator to set Access-Control-Allow
	'''
	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
		response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
		return response

	'''
	Create an endpoint to handle GET requests 
	for all available categories.
	'''
	@app.route('/categories')
	def retrieve_categories():
		categories = Category.query.order_by(Category.type).all()

		# If there are no categories, abort (not found)
		if len(categories) == 0: abort(404)

		return jsonify({
			'categories': {category.id: category.type for category in categories},
			'success': True
		})

	'''
	Create an endpoint to handle GET requests for questions, 
	including pagination (every 10 questions). 
	This endpoint should return a list of questions, 
	number of total questions, current category, categories. 
	'''
	@app.route('/questions', methods=['GET'])
	def retrieve_questions():
		selection = Question.query.order_by(Question.id).all()
		total_questions = len(selection)
		questions = paginate_questions(request, selection)

		categories = Category.query.order_by(Category.type).all()

		# If there are no questions, abort (not found)
		if len(questions) == 0: abort(404)

		return jsonify({
			'categories': {category.id: category.type for category in categories},
			'questions': questions,
			'current_category': None,
			'success': True,
			'total_questions': total_questions
			})

	'''
	Create an endpoint to DELETE question using a question ID. 

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page. 
	'''
	@app.route('/questions/<int:question_id>', methods=['DELETE'])
	def delete_question_by_id(question_id):
		try:
			question = Question.query.get(question_id)

			# If there isn't a question with that id, abort (not found)
			if question is None: abort(404)

			# Otherwise, delete the question with the matching id
			question.delete()

			return jsonify({
				'deleted': question_id,
				'success' : True				
				})

		except:
			abort(422)

	'''
	Create an endpoint to POST a new question, 
	which will require the question and answer text, 
	category, and difficulty score.
	'''
	@app.route("/questions", methods=['POST'])
	def add_question():
		body = request.get_json()

		# If there is an input category missing, abort (not processable)
		if ((body.get('question')) is None or
			(body.get('answer')) is None or
			(body.get('difficulty')) is None or
			(body.get('category')) is None):
				abort(422)

		try:
			# Insert the question with the provided information
			Question(question=body.get('question'),
		        	answer=body.get('answer'),
		        	difficulty=body.get('difficulty'),
		        	category=body.get('category')).insert()

			return jsonify({
				'created': question.id,
				'success': True
				})

		except:
			abort(422)

	'''
	Create a POST endpoint to get questions based on a search term. 
	It should return any questions for whom the search term 
	is a substring of the question. 
	'''
	@app.route('/questions/search', methods=['POST'])
	def search_questions():
		body = request.get_json()
		search_term = body.get('searchTerm', None)

		# If the search term is valid, grab the questions that match the criteria
		if search_term:
			results = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
			total_questions = len(results)
			questions = paginate_questions(request, results)

			# If the there are no questions that match the search criteria, abort (not found)
			if total_questions == 0: abort(404)

			return jsonify({
				'current_category': None,
				'questions': questions,
				'success': True,
				'total_questions': total_questions
				})

		abort(404)

	'''
	Create a GET endpoint to get questions based on category. 

	TEST: In the "List" tab / main screen, clicking on one of the 
	categories in the left column will cause only questions of that 
	category to be shown. 
	'''
	@app.route('/categories/<int:category_id>/questions', methods=['GET'])
	def retrieve_questions_by_category(category_id):
		category = Category.query.get(id)

		# If there isn't a category that matches the id, abort (not found)
		if (category is None): abort(404)

		# Otherwise, retrieve all the questions from within the category
		try:
			category_questions = Question.query.filter(Question.category == str(category_id)).all()
			total_questions = len(category_questions)
			questions = paginate_questions(request, category_questions)

			return jsonify({
				'current_category': category_id,
				'questions': questions,
				'success': True,
				'total_questions': total_questions
				})

		except:
			abort(404)

	'''
	Create a POST endpoint to get questions to play the quiz. 
	This endpoint should take category and previous question parameters 
	and return a random questions within the given category, 
	if provided, and that is not one of the previous questions. 
	'''
	@app.route('/quizzes', methods=['POST'])
	def play_quiz():
		try:
			body = request.get_json()
			previous_questions = body.get('previous_questions')
			category = body.get('quiz_category')

			# Check if quiz category and previous questions are both empty, abort (not processable)
			if (category is None and previous_questions is None): abort(422)

			category_id = int(category['id'])

			# Check to see if the user selected a category or "All"
			# If user selected a category, filter by category, and filter out previously used questions
			if category_id != 0:
				all_questions = Question.query.filter_by(category=category['id']).filter(
					Question.id.notin_((previous_questions))).all()
			# If "All", then filter out previous questions from all categories without category filter
			else:
				all_questions = Question.query.filter(
					Question.id.notin_((previous_questions))).all()

			# End the game if there are no more questions remaining
			if (len(all_questions) == 0):
				return jsonify({
					'success': True,
					'message': "game over"
					}), 200

			# Choose a random question from all the available questions
			else:
				question = random.choice(questions).format()

			return jsonify({
				'success': True,
				'question': question
				})

		except:
			abort(422)
			
	'''
		try:
			body = request.get_json()
            previous_questions_ids = body.get('previous_questions', [])
			
            quiz_category = body.get('quiz_category')

            category_id = int(quiz_category['id'])

            all_questions = Question.query.order_by(Question.id).filter(
                Question.category_id == category_id).all()

            if len(previous_questions_ids) >= len(all_questions):
                all_questions = Question.query.order_by(Question.id).all()

            random_question = {}
            while bool(random_question) is False:
                for question in all_questions:
                    if question.id not in previous_questions_ids:
                        random_question = question.format()

            data = {
                'success': True,
                'question': random_question,
                'current_category': quiz_category['type']
            }

            # send data in json format
            return jsonify(data)

        except Exception:
            abort(404)
	'''



	''' 
	Create error handlers for all expected errors 
	including 404 and 422.
	'''
	''' 400 Bad request '''
	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({
			"success": False,
			"error": 400,
			"message": "bad request"
			}), 400

	''' 404 Resource not found '''
	@app.errorhandler(404)
	def not_found(error):
		return jsonify({
			"success": False,
			"error": 404,
			"message": "resource not found"
			}), 404

	''' 405 Method not allowed '''
	@app.errorhandler(405)
	def method_not_allowed(error):
   		return jsonify({
			"success": False, 
			"error": 405,
			"message": "method not allowed"
			}), 405

	''' 422 Unprocessable '''
	@app.errorhandler(422)
	def unprocessable(error):
		return jsonify({
			"success": False,
			"error": 422,
			"message": "unprocessable"
			}), 422
  
	''' Not used '''
	''' 500 Internal Server Error
	@app.errorhandler(500)
  	def internal_server_error(error):
    	return jsonify({
      		"success": False, 
      		"error": 500,
      		"message": "internal server error"
			}), 500
	'''
	def getErrorMessage(error, default_text):
		try:
			return error.description["message"]
		except TypeError:
			return default_text
  
	return app

    