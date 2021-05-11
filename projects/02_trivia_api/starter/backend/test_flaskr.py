import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
	"""This class represents the trivia test case"""

	def setUp(self):
		"""Define test variables and initialize app."""
		self.app = create_app()
		self.client = self.app.test_client
		self.database_name = "trivia_test"
		self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
		setup_db(self.app, self.database_path)

		# binds the app to the current context
		with self.app.app_context():
			self.db = SQLAlchemy()
			self.db.init_app(self.app)
			# create all tables
			self.db.create_all()
    
	def tearDown(self):
		"""Executed after reach test"""
		pass

	"""
	Write at least one test for each test for successful operation and for expected errors.
	"""
	def test_endpoint_not_available_404(self):
		# Test GET request for the endpoint
		res = self.client().get('/question')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'resource not found')


	def test_get_categories_200(self):
		# Test GET request for all categories
		res = self.client().get('/categories')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(len(data['categories']))


	def test_get_non_existing_category_404(self):
		# Test GET request for a non-existent category
		res = self.client().get('/categories/10101')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'resource not found')


	def test_get_categories_method_error_405(self):
		# Test GET request for wrong method to get all categories 
		res = self.client().patch('/categories')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 405)
		self.assertEqual(data['message'], "method not allowed")
		self.assertEqual(data['success'], False)


	def test_get_paginated_questions_200(self):
		# Test GET request for all questions
		res = self.client().get('/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(data['total_questions'])


	def test_get_questions_past_valid_range_404(self):
		# Test GET request for questions out of range
		res = self.client().get('/questions?page=10101')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'resource not found')


	def test_add_question_200(self):
		# Test POST request for adding a new question
		old_questions = Question.query.all()

		res = self.client().post('/questions', json={
			'question': 'new question',
			'answer' : 'new answer',
			'difficulty': 1,
			'category': 1
			})
		data = json.loads(res.data)
		new_questions = Question.query.all()
        

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue((len(new_questions) - len(old_questions)) == 1)


	def test_add_question_error_422(self):
		# Test POST new question with difficulty input missing
		old_questions = Question.query.all()

		res = self.client().post('/questions', json={
			'question': 'Test Question?',
			'answer': 'Yes',
			'category': 1})
		data = json.loads(res.data)
		new_questions = Question.query.all()

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data["success"], False)
		self.assertEqual(data["message"], "unprocessable")
		self.assertTrue(len(new_questions) == len(old_questions))


	def test_delete_question_200(self):
		# Test DELETE a question
		res = self.client().delete('questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)


	def test_delete_non_existing_question_404(self):
		# Test DELETE a question that is non existent
		res = self.client().delete('/questions/a')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'resource not found')


	def test_search_question_200(self):
		# Test POST search a question with a term
		res = self.client().post('/questions/search', json={
			'searchTerm': 'z'
			})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertIsNotNone(data['questions'])
		self.assertIsNotNone(data['total_questions'])


	def test_search_question_error_404(self):
		# Test POST search a question with term not in database
		res = self.client().post('/questions/search', json={
			'searchTerm': 'z',
			})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data["success"], False)
		self.assertEqual(data["message"], "resource not found")


	def test_get_questions_per_category_200(self):
		# Test GET all questions from first category
		res = self.client().get('/categories/1/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(len(data['questions']))
		self.assertTrue(data['total_questions'])
		self.assertTrue(data['current_category'])


	def test_get_questions_per_category_404(self):
		# Test GET all questions from specified category
		res = self.client().get('/categories/a/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data["success"], False)
		self.assertEqual(data["message"], "resource not found")


	def test_play_quiz_200(self):
		# Test POST to play a new quiz
		res = self.client().post('/quizzes', json={
			'previous_questions': [],
			'quiz_category': {'type': 'Sports', 'id': 1
			}})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)


	def test_play_quiz_422(self):
		# Test POST to play a new quiz while missing data
		res = self.client().post('/quizzes', json={
			'previous_questions': []
			})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data["success"], False)
		self.assertEqual(data["message"], "unprocessable")




# Make the tests conveniently executable
if __name__ == "__main__":
	unittest.main()