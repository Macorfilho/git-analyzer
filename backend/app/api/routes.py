from flask import Blueprint, jsonify, request
from app.services.analysis_service import AnalysisService
from app.services.github_provider import GithubProvider
import os

api_bp = Blueprint('api', __name__)

def get_analysis_service():
    # Dependency Injection (Manual for this scale)
    token = os.getenv("GITHUB_TOKEN")
    provider = GithubProvider(token=token)
    return AnalysisService(provider)

@api_bp.route('/analyze/<username>', methods=['GET'])
def analyze_profile(username):
    try:
        service = get_analysis_service()
        report = service.analyze_user(username)
        return jsonify(report.dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except ConnectionError as e:
        # Simple heuristic: if "403" or "rate limit" is in the message
        if "403" in str(e) or "rate limit" in str(e).lower():
             return jsonify({"error": "GitHub API Rate Limit Exceeded. Please try again later."}), 429
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500
