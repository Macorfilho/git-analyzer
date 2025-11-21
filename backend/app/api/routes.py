from flask import Blueprint, jsonify, request
from app.redis_client import get_queue
from app.tasks import run_analysis_task
from app.job_store import JobStore
import os

api_bp = Blueprint('api', __name__)
job_store = JobStore()

@api_bp.route('/analyze/<username>', methods=['POST'])
def analyze_profile(username):
    """
    Enqueues an analysis task for the given username.
    """
    try:
        # Get query params from the POST request (or JSON body? usually params in URL or body)
        # The previous GET used request.args. Let's support JSON body for POST.
        data = request.get_json() or {}
        llm_model = data.get('model', 'llama3')
        
        # Enqueue the job
        queue = get_queue()
        job = queue.enqueue(
            run_analysis_task,
            args=(username, llm_model),
            job_timeout='10m' # Allow 10 mins for analysis
        )
        
        return jsonify({
            "message": "Analysis enqueued",
            "job_id": job.get_id(),
            "status_url": f"/api/status/{job.get_id()}"
        }), 202

    except Exception as e:
        return jsonify({"error": "Failed to enqueue job", "details": str(e)}), 500

@api_bp.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    Checks the status of a background job.
    """
    try:
        status = job_store.get_status(job_id)
        
        if status == "unknown":
            return jsonify({"error": "Job not found"}), 404
            
        response = {"job_id": job_id, "status": status}
        
        if status == "finished":
            result = job_store.get_result(job_id)
            response["result"] = result
        elif status == "failed":
            # Optionally fetch error details from job.exc_info
            job = job_store.get_job(job_id)
            response["error"] = job.exc_info if job else "Unknown error"

        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500