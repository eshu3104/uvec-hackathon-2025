from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configure CORS for session-based authentication
    CORS(app, 
         origins=['http://localhost:8080', 'http://127.0.0.1:8080'],
         supports_credentials=True)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Session configuration for cross-origin authentication
    app.config['SESSION_COOKIE_DOMAIN'] = 'localhost'
    app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allow JavaScript access for debugging
    app.config['SESSION_COOKIE_SECURE'] = False    # Allow HTTP in development
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Allow cross-origin requests
    
    # Register blueprints
    from routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Flask backend is running'
        })
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to Flask Backend API',
            'version': '1.0.0'
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
