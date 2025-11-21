from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from app.api.routes import api_bp
from app.redis_client import get_redis_connection
from redis.exceptions import ConnectionError as RedisConnectionError
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
        # Optional: Check Redis health here too
        return {"status": "ok", "message": "GitHub Profile Analyzer API is running"}

    return app

if __name__ == '__main__':
    # Initialize Redis connection check
    try:
        redis_conn = get_redis_connection()
        redis_conn.ping()
        print("✅ Connected to Redis")
    except RedisConnectionError:
        print("❌ Could not connect to Redis. Ensure Redis is running.")
        # We might want to exit or continue depending on resilience strategy. 
        # For now, we warn.

    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
