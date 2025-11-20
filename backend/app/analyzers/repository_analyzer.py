from typing import Dict, Any, List
from app.analyzers.base import BaseAnalyzer
from app.models.dtos import Repository

class RepositoryAnalyzer(BaseAnalyzer):
    """
    Analyzes a list of repositories for good practices.
    """

    def analyze(self, repositories: List[Repository]) -> Dict[str, Any]:
        """
        Analyzes a list of Repository DTOs.
        
        Checks for:
        - Descriptive README (proxy via description existence and length)
        - Commit consistency (proxy via update frequency or just mock for now)
        - Language definition
        """
        total_score = 0
        repo_count = len(repositories)
        
        if repo_count == 0:
             return {
                "score": 0,
                "issues": ["No public repositories found."]
            }

        issues = []
        
        for repo in repositories:
            repo_score = 0
            repo_max = 100
            
            # 1. Description (40 points)
            if repo.description and len(repo.description) > 10:
                repo_score += 40
            else:
                issues.append(f"Repo '{repo.name}': Missing or short description.")

            # 2. Language defined (20 points)
            if repo.language:
                repo_score += 20
            else:
                 issues.append(f"Repo '{repo.name}': Language not detected.")

            # 3. Activity/Stars (Bonus/Proxy for quality) (20 points)
            if repo.stargazers_count > 0:
                repo_score += 20
            
            # 4. Forks (Bonus) (20 points)
            if repo.forks_count > 0:
                 repo_score += 20

            # Note: A real .gitignore check requires fetching file trees, 
            # which is expensive. We skip it for this specific DTO-based implementation
            # or assume a 'has_gitignore' field might be added later.

            total_score += repo_score

        avg_score = total_score / repo_count if repo_count > 0 else 0

        return {
            "score": round(avg_score),
            "issues": issues[:10] # Limit issues to top 10 to avoid clutter
        }
