from typing import Dict, Any
from app.core.interfaces import IGithubProvider, ILLMProvider
from app.models.dtos import AnalysisReport, UserProfile, Suggestion
from app.services.insight_engine import MaturityAnalyzer, TechStackAnalyzer

class AnalysisService:
    """
    Orchestrator service that coordinates data fetching and analysis via LLM.
    """
    def __init__(self, github_provider: IGithubProvider, llm_provider: ILLMProvider):
        self.github_provider = github_provider
        self.llm_provider = llm_provider
        self.maturity_analyzer = MaturityAnalyzer()
        self.tech_stack_analyzer = TechStackAnalyzer()

    def analyze_user(self, username: str) -> AnalysisReport:
        # 1. Fetch Data
        user_profile = self.github_provider.get_user_profile(username)

        # 2. Run Insights (Maturity & Tech Stack)
        for repo in user_profile.repositories:
            score, label = self.maturity_analyzer.analyze(repo)
            repo.maturity_score = score
            repo.maturity_label = label
            
        tech_stack = self.tech_stack_analyzer.analyze(user_profile.repositories)

        # 3. Prepare Context for LLM
        context = self._prepare_context(user_profile, tech_stack)

        # 4. Generate Analysis via LLM
        llm_result = self.llm_provider.generate_analysis(context)

        # 5. Map to AnalysisReport
        details = {
            "repo_count": len(user_profile.repositories),
            "followers": user_profile.followers,
            "public_repos": user_profile.public_repos,
            "core_stack": tech_stack["core_stack"],
            "experimentation_stack": tech_stack["experimentation"],
            "career_roadmap": llm_result.get("career_roadmap", []),
            "repositories": [repo.dict() for repo in user_profile.repositories]
        }

        return AnalysisReport(
            username=user_profile.username,
            profile_score=int(llm_result.get("profile_score", 0)),
            readme_score=int(llm_result.get("readme_score", 0)),
            repo_quality_score=int(llm_result.get("repo_quality_score", 0)),
            overall_score=int(llm_result.get("overall_score", 0)),
            summary=llm_result.get("summary", "Analysis complete."),
            suggestions=[Suggestion(**s) for s in llm_result.get("suggestions", [])],
            details=details,
            raw_llm_response=llm_result
        )

    def _prepare_context(self, user: UserProfile, tech_stack: Dict[str, list]) -> str:
        """
        Formats the UserProfile into a string context for the LLM.
        """
        repo_summaries = []
        languages = set()

        for repo in user.repositories[:15]:  # Limit to top 15 to avoid token limits if needed
            if repo.language:
                languages.add(repo.language)
            
            deps_str = ", ".join(repo.dependencies[:5]) if repo.dependencies else "None detected"

            repo_summaries.append(
                f"- Name: {repo.name}\n"
                f"  Language: {repo.language}\n"
                f"  Description: {repo.description or 'MISSING DESCRIPTION (High negative signal)'}\n"
                f"  Stars: {repo.stargazers_count} | Forks: {repo.forks_count}\n"
                f"  Last Updated: {repo.updated_at}\n"
                f"  Maturity: {repo.maturity_label} (Score: {repo.maturity_score})\n"
                f"  Signals: CI={repo.has_ci}, Tests={repo.has_tests}, Docker={repo.has_docker}, License={repo.has_license}\n"
                f"  Dependencies: {deps_str}"
            )
        
        repos_text = "\n".join(repo_summaries) if repo_summaries else "No public repositories found."
        detected_languages = ", ".join(sorted(languages)) if languages else "None detected"
        
        core_stack_str = ", ".join(tech_stack["core_stack"]) if tech_stack["core_stack"] else "None identified"
        exp_stack_str = ", ".join(tech_stack["experimentation"]) if tech_stack["experimentation"] else "None identified"

        context = (
            f"User: {user.username}\n"
            f"Name: {user.name or 'N/A'}\n"
            f"Bio: {user.bio or 'N/A'}\n"
            f"Location: {user.location or 'N/A'}\n"
            f"Followers: {user.followers} | Following: {user.following}\n"
            f"Public Repos: {user.public_repos}\n"
            f"Detected Languages: {detected_languages}\n"
            f"Core Tech Stack (Production-Ready): {core_stack_str}\n"
            f"Experimental Tech Stack: {exp_stack_str}\n\n"
            f"--- Repositories (Top 15) ---\n"
            f"{repos_text}\n\n"
            f"--- Main Profile README ---\n"
            f"{user.readme_content or 'No README content available.'}"
        )
        return context