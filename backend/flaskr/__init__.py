import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category
from paginate import paginate
from dotenv import load_dotenv
load_dotenv('../.env')

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()

        if not len(categories):
            abort(404)
        else:
            return jsonify({
                "status": True,
                'categories': {category.id: category.type for category in categories}
            }), 200
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=["GET"])
    def get_questions():
        questions = Question.query.all()
        page_number = request.args.get("page", 1, type=int)
        questions = paginate(questions,  QUESTIONS_PER_PAGE, page_number)
        categories = Category.query.all()

        if not len(questions):
            abort(404)

        return jsonify({
            "status": True,
            "questions": questions,
            "total_questions": len(questions),
            "categories": {category.id: category.type for category in categories},
            # "currentCategory": "History"
        }), 200

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()

            if question is None:
                abort(404)
            question.delete()
        except:
            abort(422)

        return jsonify({
            "status": True,
            "message": 'Deleted successfully',
            "question_id": id
        }), 204

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.


    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    # AND

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST'])
    def new_question():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)
        search_term = body.get('searchTerm', None)

        if search_term is not None:
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            questions = [question.format() for question in questions]
            return jsonify({
                "status": True,
                "questions": questions,
                "totalQuestions": len(questions),
                "currentCategory": None
            }), 200
        else:
            try:
                if not question or not answer or not difficulty or not category:
                    return jsonify({"status": False, "message": 'All fields are required'}), 400

                difficulty = int(difficulty)
                question = Question(question=question, answer=answer,
                                    difficulty=difficulty, category=category)
                question.insert()
                return jsonify({
                    'status': True,
                    "message": 'Question added successfully'
                }), 201
            except:
                abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        questions = None
        try:
            questions = Question.query.filter(
                Question.category == str(category_id)).all()
            questions = paginate(questions, QUESTIONS_PER_PAGE)
            if len(questions) == 0:
                abort(404)
        except:
            abort(422)

        return jsonify({
            "status": True,
            "questions": questions,
            "totalQuestions": len(questions),
            "currentCategory": None
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        body = request.get_json()
        quiz_category = body.get("quiz_category", None)
        previous_questions = body.get("previous_questions", None)

        if len(body) == 0:
            abort(400)

        if (quiz_category['type'] == 'click'):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(
                category=quiz_category['id']).all()

        def generate_question():
            return questions[random.randrange(0, len(questions))].format()

        total_questions = len(questions)
        question = generate_question()

        def check_for_prev_question(num):
            is_prev_question = False
            for i in previous_questions:
                if i == num:
                    is_prev_question = True
            return is_prev_question

        while check_for_prev_question(question['id']):
            question = generate_question()

            if (len(previous_questions) == total_questions):
                return jsonify({
                    'status': True
                })

        return jsonify({
            "status": True,
            "question": question
        }), 200

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(422)
    def err(error):
        return jsonify({
            "status": False,
            "message": "Not found"
        }), 404

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": False,
            "message": "Not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "status": False,
            "message": "Bad request"
        }), 400

    @app.errorhandler(405)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message": "Request Method not allowed"
        }), 400

    return app
