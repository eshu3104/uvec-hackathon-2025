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
         origins=['http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:8081', 'http://127.0.0.1:8081', 'http://134.87.58.50:8080', 'http://134.87.58.50:8081'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-very-long-and-secure-key-for-development-only')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Session configuration for cross-origin authentication
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow all domains in development
    app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allow JavaScript access for debugging
    app.config['SESSION_COOKIE_SECURE'] = False    # Allow HTTP in development
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Use Lax for better compatibility
    app.config['SESSION_COOKIE_PATH'] = '/'  # Set explicit path
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    # Remove custom session name to use default 'session'
    
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
