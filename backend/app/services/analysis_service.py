from typing import Dict, Any
from app.core.interfaces import IGithubProvider, ILLMProvider
from app.models.dtos import AnalysisReport, UserProfile, Suggestion
from app.services.insight_engine import MaturityAnalyzer, TechStackAnalyzer, RepoDocumentationAnalyzer, CommitHygieneAnalyzer, ProfileReadmeAnalyzer
from app.services.collectors import StructureCollector, DependencyCollector

class AnalysisService:
    """
    Orchestrator service that coordinates data fetching and analysis via LLM.
    """
    def __init__(self, github_provider: IGithubProvider, llm_provider: ILLMProvider):
        self.github_provider = github_provider
        self.llm_provider = llm_provider
        self.maturity_analyzer = MaturityAnalyzer()
        self.tech_stack_analyzer = TechStackAnalyzer()
        self.repo_doc_analyzer = RepoDocumentationAnalyzer()
        self.commit_hygiene_analyzer = CommitHygieneAnalyzer()
        self.profile_readme_analyzer = ProfileReadmeAnalyzer()
        
        # Collectors
        self.structure_collector = StructureCollector()
        self.dependency_collector = DependencyCollector()

    def analyze_user(self, username: str) -> AnalysisReport:
        # 1. Fetch Data
        user_profile = self.github_provider.get_user_profile(username)

        # 2. Run Insights (Maturity & Tech Stack)
        total_repo_doc_score = 0
        total_code_hygiene_score = 0
        for repo in user_profile.repositories:
            # Run Collectors
            # Structure
            # Updated to use file_tree
            struct_flags = self.structure_collector.analyze(repo.file_tree)
            repo.has_ci = struct_flags["has_ci"]
            repo.has_docker = struct_flags["has_docker"]
            repo.has_tests = struct_flags["has_tests"]
            repo.has_license = struct_flags["has_license"]
            
            # Dependencies
            # DependencyCollector now accepts the dependency_files dictionary directly
            repo.dependencies = self.dependency_collector.analyze(repo.dependency_files)
            
            # Git History (Commit Hygiene)
            # Replaced GitHistoryCollector with CommitHygieneAnalyzer
            hygiene_label, cc_ratio, avg_days, hygiene_score = self.commit_hygiene_analyzer.analyze(repo.commit_history)
            repo.commit_frequency = avg_days # Renaming variable usage logic if needed, but avg_days matches conceptually roughly or we adapt
            repo.conventional_commits_ratio = cc_ratio
            repo.code_hygiene_score = hygiene_score
            total_code_hygiene_score += hygiene_score
            # Note: average_message_length is no longer computed by CommitHygieneAnalyzer in this spec,
            # but we can leave it as default or compute it if strictly needed. For now, we'll trust the new analyzer's focus.
            
            # Repo Documentation
            repo.repo_documentation_score = self.repo_doc_analyzer.analyze(repo)
            total_repo_doc_score += repo.repo_documentation_score
            
            # Maturity
            score, label = self.maturity_analyzer.analyze(repo)
            repo.maturity_score = score
            repo.maturity_label = label
            
        tech_stack = self.tech_stack_analyzer.analyze(user_profile.repositories)
        
        # Calculate Aggregates
        avg_repo_docs_score = 0
        avg_code_hygiene_score = 0
        if user_profile.repositories:
            avg_repo_docs_score = int(total_repo_doc_score / len(user_profile.repositories))
            avg_code_hygiene_score = int(total_code_hygiene_score / len(user_profile.repositories))
            
        # Analyze Personal README
        personal_readme_score = self.profile_readme_analyzer.analyze(user_profile.readme_content or "")

        # 3. Prepare Context for LLM
        context = self._prepare_context(user_profile, tech_stack, avg_repo_docs_score, personal_readme_score, avg_code_hygiene_score)

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
            avg_repo_docs_score=avg_repo_docs_score,
            personal_readme_score=personal_readme_score,
            repo_quality_score=int(llm_result.get("repo_quality_score", 0)),
            overall_score=int(llm_result.get("overall_score", 0)),
            summary=llm_result.get("summary", "Analysis complete."),
            suggestions=[Suggestion(**s) for s in llm_result.get("suggestions", [])],
            details=details,
            raw_llm_response=llm_result,
            avg_code_hygiene_score=avg_code_hygiene_score
        )

    def _prepare_context(self, user: UserProfile, tech_stack: Dict[str, list], avg_doc_score: int, personal_readme_score: int, avg_code_hygiene_score: int) -> str:
        """
        Formats the UserProfile into a rich, narrative context for the LLM to reduce hallucinations.
        """
        from datetime import datetime, timezone
        
        repo_narratives = []
        
        repos_with_ci = sum(1 for r in user.repositories if r.has_ci)
        repos_with_tests = sum(1 for r in user.repositories if r.has_tests)
        
        current_time = datetime.now(timezone.utc)

        # Generate Narrative Summaries
        for repo in user.repositories[:15]:
            # 1. Determine Status & Staleness
            last_update_dt = None
            try:
                 last_update_dt = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
                 if last_update_dt.tzinfo is None:
                     last_update_dt = last_update_dt.replace(tzinfo=timezone.utc)
            except:
                pass
            
            days_since_update = (current_time - last_update_dt).days if last_update_dt else 9999
            status_str = "Active"
            if days_since_update > 365:
                status_str = "Ghost/Archived"
            
            # 2. Construct Narrative Line
            # Stack info
            stack_items = [repo.language] + repo.dependencies[:5]
            stack_str = ", ".join(filter(None, stack_items))
            
            # Maturity & Hygiene labels
            maturity_info = f"{repo.maturity_label} (Score: {repo.maturity_score})"
            
            hygiene_label_from_score = "Messy"
            if repo.code_hygiene_score >= 80:
                hygiene_label_from_score = "Professional"
            elif repo.code_hygiene_score >= 60:
                hygiene_label_from_score = "Hygiene"
            elif repo.code_hygiene_score >= 40:
                hygiene_label_from_score = "Active"
            
            # Docs Details
            docs_label = "Weak"
            docs_missing = []
            if repo.repo_documentation_score > 80:
                docs_label = "Strong"
            elif repo.repo_documentation_score > 50:
                docs_label = "Adequate"
            
            # Check for missing specific sections based on score content
            # Since we don't store the missing headers in DTO, we re-check or infer.
            # Ideally, Analyzer should return metadata. For now, we check raw content quickly if available.
            if repo.readme_content:
                lower_readme = repo.readme_content.lower()
                if "usage" not in lower_readme:
                    docs_missing.append("'Usage'")
                if "installation" not in lower_readme and "getting started" not in lower_readme:
                    docs_missing.append("'Installation'")
            
            docs_detail = f"{docs_label} (Score: {repo.repo_documentation_score})"
            if docs_missing:
                docs_detail += f" (Missing {', '.join(docs_missing)} section)"
            
            # 3. Explicit Signals (Ghost / Red Flags)
            prefix = ""
            
            # Ghost Project: Low maturity & inactive > 1 year
            if repo.maturity_score < 30 and days_since_update > 365:
                prefix = "[GHOST PROJECT] "
                status_str = "Ghost"

            # Final Line Construction
            line = (
                f"{prefix}Repo: {repo.name} | "
                f"Stack: {stack_str} | "
                f"Maturity: {maturity_info} | "
                f"Docs: {docs_detail} | "
                f"Hygiene: {hygiene_label_from_score} (Score: {repo.code_hygiene_score}) | "
                f"Status: {status_str} (Updated {days_since_update} days ago)"
            )
            repo_narratives.append(line)
        
        repos_text = "\n".join(repo_narratives) if repo_narratives else "No public repositories found."
        
        # Tech Stack Aggregation
        core_stack = tech_stack.get("core_stack", [])
        dabbling_stack = tech_stack.get("experimentation", [])
        primary_ecosystem = ', '.join(core_stack) if core_stack else 'None identified'
        
        context = (
            f"REPORT FOR USER: {user.username}\n"
            f"BIO: {user.bio or 'No bio provided'}\n\n"
            f"--- PORTFOLIO ANALYSIS ---\n"
            f"- Total Repositories: {len(user.repositories)}\n"
            f"- Total Repos with CI/CD: {repos_with_ci}/{len(user.repositories)}\n"
            f"- Total Repos with Tests: {repos_with_tests}/{len(user.repositories)}\n"
            f"- Primary Ecosystem: {primary_ecosystem}\n"
            f"- Average Repo Documentation Score: {int(avg_doc_score)}/100\n"
            f"- Personal Profile README Score: {personal_readme_score}/100\n"
            f"- Average Code Hygiene Score: {avg_code_hygiene_score}/100\n"
            f"- Experimental Tech: {', '.join(dabbling_stack) if dabbling_stack else 'None'}\n\n"
            f"--- REPOSITORY NARRATIVES ---\n"
            f"{repos_text}\n\n"
            f"--- INSTRUCTIONS FOR ANALYSIS ---\n"
            f"Based ONLY on the above data, analyze the user's profile. \n"
            f"1. Ignore 'Ghost Projects' for current skill estimation.\n"
            f"2. Penalize 'Red Flags' heavily in the Quality Score.\n"
            f"3. Highlight 'Production-Grade' habits (CI/CD, Tests, Documentation) as key strengths."
        )
        return context
