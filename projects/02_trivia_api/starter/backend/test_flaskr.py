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
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_endpoint_not_available(self):
        # Test GET request for the endpoint
        res = self.client().get('/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found, endpoint not available')


    def test_get_categories_200(self):
        # Test GET request for all categories
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))


    def test_get_non_existing_category_404(self):
        # Test GET request for a non-existent category
        res = self.client().get('/categories/999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_get_categories_method_error_405(self):
        # Test GET request for wrong method to get all categories 
        res = self.client().patch('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], "method not allowed")
        self.assertEqual(data['success'], False)


    def test_get_paginated_questions_200(self):
        # Test GET request for all questions
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))


    def test_get_questions_past_valid_range_404(self):
        # Test GET request for questions out of range
        res = self.client().get('/questions?page=1234')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_add_question_200(self):
        # Test POST request for adding a new question
        old_total_questions = len(Question.query.all())

        new_question = {
            'question': 'new question',
            'answer' : 'new answer',
            'difficulty': 1, # defaults are 1
            'category': 1}

        res = self.client().post('/question', json=new_question)
        data = json.loads(res.data)
        new_total_questions = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue((len(new_total_questions) - len(old_total_questions)) == 1)


    def test_add_question_error_400(self):
        # Test POST new question with difficulty input missing
        old_total_questions = len(Question.query.all())

        new_question = {
            'question': 'Test Question?',
            'answer': 'Yes',
            'category': 1}

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        new_total_questions = len(Question.query.all())

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable, missing difficulty input")
        self.assertTrue(len(new_total_questions) == len(old_total_questions))


    def test_delete_question_200(self):
        # Test DELETE a question
        question = Question(question='test question',
                            answer='test answer',
                            difficulty=1, category=1) # default values set to 1
        question.insert()
        question_id = question.id

        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)


    def test_delete_non_existing_question_422(self):
        # Test DELETE a question that is non existent
        res = self.client().delete('/questions/a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    def test_search_question_200(self):
        # Test POST search a question with a term
        new_search = {'searchTerm': 'a'}
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])


    def test_search_question_error_404(self):
        # Test POST search a question with term not in database
        new_search = {'searchTerm': '',}
        res = self.client().post('/questions/search', json=new_search)
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
        new_quiz_round = {
            'previous_questions': [],
            'quiz_category': {'type': 'Entertainment', 'id': 5}}

        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_play_quiz_404(self):
        # Test POST to play a new quiz while missing data
        new_quiz_round = {'previous_questions': []}
        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()