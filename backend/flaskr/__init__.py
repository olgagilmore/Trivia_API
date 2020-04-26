import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

questions_played = []


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
  
    '''
    @DONE: Set up CORS. Allow '*' for origins. 
    Delete the sample route after completing the TODOs
    '''
    #   CORS(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @DONE: Use the after_request decorator to set Access-Control-Allow
    '''
    # CORS Headers 
    @app.after_request
    def after_request(response):
        # response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    
    '''
    @DONE: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all() # order_by(Category.id).all()
        # formatted_categories= [cat.format() for cat in categories]
        formatted_categories = [cat.type for cat in categories]
        
        if len(formatted_categories) == 0:
            abort(404)
          
        return jsonify({
          'success': True,
          'categories': formatted_categories,
          'total_categories': len(Category.query.all())
        }) 

    '''
    @DONE: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions', methods= ['GET'])
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        
        
        if len(current_questions) == 0:
            abort(404)
          
        categories = Category.query.all()
        
        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(Question.query.all()),
          'categories': [x.type for x in categories],
          # 'currentCategory': result.current_category
        })    
          
    '''
    @DONE: 
    Create an endpoint to DELETE question using a question ID. 
    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
        
            if question is None:
                abort(404)
        
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
        
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        
        except:
            abort(422)


    '''
    @DONE: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
            
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        
        search = body.get('searchTerm', None)
    
        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
                # current_questions = paginate_questions(request, selection)
                current_questions= [q.format() for q in selection]
                
                return jsonify({
                  'success': True,
                  
                  'questions': current_questions,
                  'totalQuestions': len(selection.all())
                })
    
            else: 
    
                question = Question(question=new_question, answer=new_answer, 
                                    category=int(new_category)+1, difficulty=new_difficulty)
                question.insert()
                
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)
                
                return jsonify({
                  'success': True,
                  'created': question.id,
                  'questions': current_questions,
                  'totalQuestions': len(Question.query.all())
                })
    
        except:
            abort(422)
      
    '''
    @DONE: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
    
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    
    Search is implemented as part create_question method
    '''

    '''
    @DONE: 
    Create a GET endpoint to get questions based on category. 
    
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def get_questions_per_category(cat_id):
        # Category is a foreign key for question table
        # cat_questions= Question.query.join(Category, Question.category==Category.id).filter(Category.type==cat_type).all()
        cat_id += 1
        cat_questions= Question.query.join(Category, Question.category==Category.id).filter(Category.id==cat_id).all()
        
        formatted_questions=[q.format() for q in cat_questions]
        
        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'category': cat_id,
          'total_questions': len(cat_questions)
        })   
        
    
    '''
    @DONE: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
    
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
        
    @app.route('/quizzes', methods=['POST'])   
    def play_quizz(): 
        content = request.json
        q_category= int(content['quiz_category']["id"]) + 1
        prev_questions= content["previous_questions"]
        numeric_prev_questions= [int(numeric_string) for numeric_string in prev_questions]
        
        cat_questions= Question.query.join(Category, Question.category==Category.id).filter(Category.id==q_category).all()
        
        not_played = [x for x in cat_questions if x.id not in numeric_prev_questions]
        
        random_question = random.choice(not_played)
        
        return jsonify({
            "success": True,
            "question": random_question.format()
            })
        
        
    '''
    @DONE: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
            }), 404
            
    @app.errorhandler(422)
    def notprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
            }), 422
            
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
            }), 400
            
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
            }), 500      
            
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
            }), 405     
  
    return app

    