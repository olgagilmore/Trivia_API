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
        self.database_name = "test_trivia"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'dbadmin', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            
        self.new_question= {
            'question': "What is Earth?",
            'answer': "planet",
            'difficulty': "1",
            'category': "1"
            }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        response= self.client().get('/questions')
        data= json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        
    def test_404_requesting_beyond_valid_page(self):
        response= self.client().get('/questions?page=1000', json={'question':"Nothing"})
        data= json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")
        
    def test_get_categories(self):
        response= self.client().get('/categories')
        data= json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))    
        
    def test_get_questions_per_category(self):
        response= self.client().get('categories/2/questions')
        data= json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['category'], 3)        
        self.assertTrue(len(data['questions']))
        
    def test_create_question(self):
        response= self.client().post('/questions', json= self.new_question)
        data= json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        
        self.assertTrue(data['totalQuestions'])        
        self.assertTrue(len(data['questions']))      
        
    def test_delete_questions(self):
        response= self.client().delete('/questions/57')
        data= json.loads(response.data)

        quest= Question.query.filter(Question.id==57).one_or_none()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'],57)
        self.assertEqual(quest, None)
        self.assertTrue(data['total_questions'])        
        self.assertTrue(len(data['questions']))
        
    def test_delete_questions_out_of_bounds(self):
        response= self.client().delete('/questions/1000')
        data= json.loads(response.data)

        quest= Question.query.filter(Question.id==1000).one_or_none()
        
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        
    
        
    def test_post_not_allowed(self):
        response= self.client().post('/questions/42', json= self.new_question)
        data= json.loads(response.data)
        
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')
        
    def test_search_with_results(self):
        response= self.client().post('/questions', json= {'searchTerm':'Which'})
        data= json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
        self.assertEqual(data['totalQuestions'],5)        
        self.assertTrue(len(data['questions']))  
        
    def test_search_no_results(self):
        response= self.client().post('/questions', json= {'searchTerm':'wwwww'})
        data= json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
        self.assertEqual(data['totalQuestions'],0)        
        self.assertEqual(len(data['questions']),0)  
        
#     def test_post_not_allowed(self):
#         response= self.client().post('/questions/42', json= self.new_question)
#         data= json.loads(response.data)
#         
#         self.assertEqual(response.status_code, 405)
#         self.assertEqual(data['success'], False)
#         self.assertEqual(data['message'], 'method not allowed')    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()