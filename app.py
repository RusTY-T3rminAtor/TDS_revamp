from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from quiz_solver import QuizSolver
import threading

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
STUDENT_EMAIL = os.getenv('STUDENT_EMAIL')
SECRET_KEY = os.getenv('SECRET_KEY')
PORT = int(os.getenv('PORT', 5000))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/quiz', methods=['POST'])
def receive_quiz():
    """
    Main endpoint to receive quiz tasks
    Expected payload:
    {
        "email": "student email",
        "secret": "student secret",
        "url": "quiz URL"
    }
    """
    try:
        # Parse JSON payload
        data = request.get_json()
        
        if not data:
            logger.error("Invalid JSON payload received")
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Extract required fields
        email = data.get('email')
        secret = data.get('secret')
        quiz_url = data.get('url')
        
        # Validate required fields
        if not all([email, secret, quiz_url]):
            logger.error("Missing required fields")
            return jsonify({"error": "Missing required fields: email, secret, url"}), 400
        
        # Verify secret
        if secret != SECRET_KEY:
            logger.error(f"Invalid secret provided for email: {email}")
            return jsonify({"error": "Invalid secret"}), 403
        
        # Verify email matches
        if email != STUDENT_EMAIL:
            logger.warning(f"Email mismatch: expected {STUDENT_EMAIL}, got {email}")
        
        logger.info(f"Received valid quiz request for URL: {quiz_url}")
        
        # Start quiz solving in background thread
        solver = QuizSolver(email, secret)
        thread = threading.Thread(target=solver.solve_quiz_chain, args=(quiz_url,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "accepted",
            "message": "Quiz solving started"
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing quiz request: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "service": "LLM Analysis Quiz Solver",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "quiz": "/quiz (POST)"
        }
    }), 200

if __name__ == '__main__':
    logger.info(f"Starting Flask server on port {PORT}")
    logger.info(f"Configured for email: {STUDENT_EMAIL}")
    app.run(host='0.0.0.0', port=PORT, debug=os.getenv('DEBUG', 'False').lower() == 'true')
