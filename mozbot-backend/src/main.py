import os
import sys
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.config import Config
from src.models import db

# Import all models
from src.models.user import User
from src.models.tenant import Tenant, UserTenant
from src.models.chatbot import Chatbot
from src.models.conversation import Conversation, Message
from src.models.automation import AutomationWorkflow, AutomationExecution

# Import blueprints
from src.routes.auth import auth_bp
from src.routes.chatbots import chatbots_bp
from src.routes.automations import automations_bp
from src.routes.channels import channels_bp

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(chatbots_bp, url_prefix='/api/v1/chatbots')
    app.register_blueprint(automations_bp, url_prefix='/api/v1/automations')
    app.register_blueprint(channels_bp, url_prefix='/api/v1/channels')
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    # Health check endpoint
    @app.route('/api/v1/health')
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'mozbot-backend'})
    
    # API info endpoint
    @app.route('/api/v1/info')
    def api_info():
        return jsonify({
            'service': 'MozBot Backend API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/v1/auth',
                'chatbots': '/api/v1/chatbots',
                'automations': '/api/v1/automations',
                'channels': '/api/v1/channels'
            }
        })
    
    # Serve frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)



