import os
from app.services.analysis_service import AnalysisService
from app.services.github_provider import GithubProvider
from app.services.llm_provider import OllamaProvider

def run_analysis_task(username: str, model_name: str = "llama3"):
    """
    Background task to run the analysis.
    """
    try:
        # Dependency Injection
        token = os.getenv("GITHUB_TOKEN")
        github_provider = GithubProvider(token=token)
        llm_provider = OllamaProvider(model=model_name)
        service = AnalysisService(github_provider, llm_provider)
        
        # Run analysis
        report = service.analyze_user(username)
        
        # Return dict for pickling
        return report.dict()
    except Exception as e:
        # RQ will catch this and mark job as failed, but we can log it
        print(f"Task failed for user {username}: {e}")
        raise e
