
import sys
import os
from dotenv import load_dotenv

# Load env vars from backend/.env
load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.github_provider import GithubProvider
from app.services.analysis_service import AnalysisService
from app.services.llm_provider import OllamaProvider

def debug_full_flow(username):
    print(f"--- Debugging User: {username} ---")
    
    # 1. Check Token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("WARNING: GITHUB_TOKEN not found in environment.")
    else:
        print(f"GITHUB_TOKEN found (length: {len(token)})")

    # 2. Fetch Data
    try:
        gh_provider = GithubProvider(token=token)
        user_profile = gh_provider.get_user_profile(username)
        print(f"Fetched Profile: {user_profile.username}")
        print(f"Public Repos: {user_profile.public_repos}")
        print(f"Repos fetched count: {len(user_profile.repositories)}")
        if user_profile.repositories:
            print(f"Sample Repo: {user_profile.repositories[0].name}")
    except Exception as e:
        print(f"GitHub Fetch Failed: {e}")
        return

    # 3. Prepare Context
    llm_provider = OllamaProvider(model="llama3")
    service = AnalysisService(gh_provider, llm_provider)
    context = service._prepare_context(user_profile)
    print("\n--- Generated Context (First 500 chars) ---")
    print(context[:500])
    print(" কুক\n")

    # 4. Call LLM
    print("--- Calling Ollama ---")
    try:
        result = llm_provider.generate_analysis(context)
        print("--- LLM Result ---")
        print(result)
    except Exception as e:
        print(f"LLM Failed: {e}")

if __name__ == "__main__":
    # Test with a known user, e.g., 'octocat' or the user's own username if known.
    # I'll use 'octocat' as a standard test.
    debug_full_flow("octocat")
