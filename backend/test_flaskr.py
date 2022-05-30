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
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
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

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], True)

    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_page_limit(self):
        response = self.client().get('/questions?page=5000')
        data = json.loads(response.data)

        self.assertEqual(data['status'], False)
        self.assertEqual(data['message'], 'Not found')
        self.assertEqual(response.status_code, 404)

    def test_delete_question(self):
        question = Question(question='What is tolulope age',
                            answer='No way', difficulty=1, category=1)
        question.insert()

        id = question.id

        response = self.client().delete(f'/questions/{id}')
        self.assertEqual(response.status_code, 204)

    def test_delete_question_fail(self):
        response = self.client().delete('/questions/50000')
        self.assertEqual(response.status_code, 404)

    def test_add_question(self):
        new_question = {
            'question': 'What is tolulope age',
            'answer': 'No way',
            'difficulty': 1,
            'category': 1
        }
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], True)
        self.assertEqual(data['message'], 'Question added successfully')

    def test_add_question_fail(self):
        new_question = {
            'question': 'what is javascript',
            'answer': 'is a programming language',
            'category': 2
        }
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["status"], False)
        self.assertEqual(data["message"], 'All fields are required')

    def test_search_question(self):
        response = self.client().post(
            '/questions', json={'searchTerm': 'what is tolulope age'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])

    def test_search_question_fail(self):
        response = self.client().post(
            '/questions', json={'searchTerm': 'Nothing is there'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(len(data['questions']) == 0)
        self.assertTrue(data['totalQuestions'] == 0)

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])

    def test_get_questions_by_category_fail(self):
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['status'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_quizzes(self):
        response = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'type': 'Entertainment',
                'id': 5
            }
        })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(data['question'])

    def test_quizzes_fail(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
