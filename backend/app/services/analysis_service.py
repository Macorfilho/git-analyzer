from typing import Dict, Any
from app.core.interfaces import IGithubProvider, ILLMProvider
from app.models.dtos import AnalysisReport, UserProfile, Suggestion

class AnalysisService:
    """
    Orchestrator service that coordinates data fetching and analysis via LLM.
    """
    def __init__(self, github_provider: IGithubProvider, llm_provider: ILLMProvider):
        self.github_provider = github_provider
        self.llm_provider = llm_provider

    def analyze_user(self, username: str) -> AnalysisReport:
        # 1. Fetch Data
        user_profile = self.github_provider.get_user_profile(username)

        # 2. Prepare Context for LLM
        context = self._prepare_context(user_profile)

        # 3. Generate Analysis via LLM
        llm_result = self.llm_provider.generate_analysis(context)

        # 4. Map to AnalysisReport
        # Ensure the LLM response has the expected fields, providing defaults if necessary
        # We cast scores to int() to handle cases where LLM returns floats (e.g., 87.5)
        return AnalysisReport(
            username=user_profile.username,
            profile_score=int(llm_result.get("profile_score", 0)),
            readme_score=int(llm_result.get("readme_score", 0)),
            repo_quality_score=int(llm_result.get("repo_quality_score", 0)),
            overall_score=int(llm_result.get("overall_score", 0)),
            summary=llm_result.get("summary", "Analysis complete."),
            suggestions=[Suggestion(**s) for s in llm_result.get("suggestions", [])],
            details={
                "repo_count": len(user_profile.repositories),
                "followers": user_profile.followers,
                "public_repos": user_profile.public_repos
            },
            raw_llm_response=llm_result
        )

    def _prepare_context(self, user: UserProfile) -> str:
        """
        Formats the UserProfile into a string context for the LLM.
        """
        repo_summaries = []
        for repo in user.repositories[:15]:  # Limit to top 15 to avoid token limits if needed
            repo_summaries.append(
                f"- Name: {repo.name}\n"
                f"  Language: {repo.language}\n"
                f"  Description: {repo.description or 'No description'}\n"
                f"  Stars: {repo.stargazers_count} | Forks: {repo.forks_count}\n"
                f"  Last Updated: {repo.updated_at}"
            )
        
        repos_text = "\n".join(repo_summaries) if repo_summaries else "No public repositories found."

        context = (
            f"User: {user.username}\n"
            f"Name: {user.name or 'N/A'}\n"
            f"Bio: {user.bio or 'N/A'}\n"
            f"Location: {user.location or 'N/A'}\n"
            f"Followers: {user.followers} | Following: {user.following}\n"
            f"Public Repos: {user.public_repos}\n\n"
            f"--- Repositories (Top 15) ---\n"
            f"{repos_text}\n\n"
            f"--- Main Profile README ---\n"
            f"{user.readme_content or 'No README content available.'}"
        )
        return context
