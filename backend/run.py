from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from app.api.routes import api_bp
import os

load_dotenv()  # Load environment variables from .env file

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all domains on all routes under /api/*
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def health_check():
        return {"status": "ok", "message": "GitHub Profile Analyzer API is running"}

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
