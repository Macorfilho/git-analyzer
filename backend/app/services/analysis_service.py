from app.core.interfaces import IGithubProvider
from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.analyzers.repository_analyzer import RepositoryAnalyzer
from app.services.suggestion_engine import SuggestionEngine
from app.models.dtos import AnalysisReport, Suggestion

class AnalysisService:
    """
    Orchestrator service that coordinates data fetching and analysis.
    """
    def __init__(self, github_provider: IGithubProvider):
        self.github_provider = github_provider
        self.profile_analyzer = ProfileAnalyzer()
        self.repo_analyzer = RepositoryAnalyzer()
        self.suggestion_engine = SuggestionEngine()

    def analyze_user(self, username: str) -> AnalysisReport:
        # 1. Fetch Data
        user_profile = self.github_provider.get_user_profile(username)

        # 2. Analyze Profile
        profile_results = self.profile_analyzer.analyze(user_profile)
        
        # 3. Analyze Repositories
        repo_results = self.repo_analyzer.analyze(user_profile.repositories)

        # 4. Generate Suggestions
        suggestions = self.suggestion_engine.generate_suggestions(user_profile.repositories)
        
        # Add analysis issues as suggestions if needed or keep separate
        for issue in repo_results.get("issues", []):
             suggestions.append(Suggestion(category="Repository Issue", severity="medium", message=issue))

        for missing in profile_results.get("missing_elements", []):
            suggestions.append(Suggestion(category="Profile Missing", severity="high", message=f"Add {missing} to your profile."))

        # 5. Calculate Overall Score (Simple Average for now)
        overall_score = int((profile_results["score"] + repo_results["score"]) / 2)

        return AnalysisReport(
            username=user_profile.username,
            profile_score=profile_results["score"],
            readme_score=profile_results["score"], # Using profile score as proxy for now, or split logic
            repo_quality_score=repo_results["score"],
            overall_score=overall_score,
            summary=f"Profile analysis for {username} complete.",
            suggestions=suggestions,
            details={
                "profile_details": profile_results["details"],
                "repo_count": len(user_profile.repositories)
            }
        )
