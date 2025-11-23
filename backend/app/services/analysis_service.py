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
        
        from app.models.dtos import ScoreDetail

        # 2. Run Insights (Maturity & Tech Stack)
        repo_docs_values = []
        repo_docs_pros = set()
        repo_docs_cons = set()
        
        hygiene_values = []
        hygiene_pros = set()
        hygiene_cons = set()
        
        for repo in user_profile.repositories:
            # Run Collectors
            struct_flags = self.structure_collector.analyze(repo.file_tree)
            repo.has_ci = struct_flags["has_ci"]
            repo.has_docker = struct_flags["has_docker"]
            repo.has_tests = struct_flags["has_tests"]
            repo.has_license = struct_flags["has_license"]
            
            repo.dependencies = self.dependency_collector.analyze(repo.dependency_files)
            
            # Git History (Commit Hygiene)
            hygiene_detail, cc_ratio, avg_days = self.commit_hygiene_analyzer.analyze(repo.commit_history)
            repo.commit_frequency = avg_days
            repo.conventional_commits_ratio = cc_ratio
            repo.code_hygiene_score = hygiene_detail
            repo.recommendations.extend(hygiene_detail.cons) # Add hygiene gaps to recommendations
            
            hygiene_values.append(hygiene_detail.value)
            hygiene_pros.update(hygiene_detail.pros)
            hygiene_cons.update(hygiene_detail.cons)
            
            # Repo Documentation
            doc_detail = self.repo_doc_analyzer.analyze(repo)
            repo.repo_documentation_score = doc_detail
            
            repo_docs_values.append(doc_detail.value)
            repo_docs_pros.update(doc_detail.pros)
            repo_docs_cons.update(doc_detail.cons)
            
            # Maturity
            maturity_detail = self.maturity_analyzer.analyze(repo)
            repo.maturity_score = maturity_detail
            repo.maturity_label = maturity_detail.label
            repo.recommendations.extend(maturity_detail.cons) # Add maturity gaps to recommendations
            
        tech_stack = self.tech_stack_analyzer.analyze(user_profile.repositories)
        
        # Calculate Aggregates for AnalysisReport
        
        # Avg Repo Docs
        avg_doc_val = int(sum(repo_docs_values) / len(repo_docs_values)) if repo_docs_values else 0
        avg_doc_detail = ScoreDetail(
            value=avg_doc_val,
            label="Average",
            pros=list(repo_docs_pros)[:5], # Top 5 unique pros
            cons=list(repo_docs_cons)[:5]
        )
        
        # Avg Hygiene
        avg_hyg_val = int(sum(hygiene_values) / len(hygiene_values)) if hygiene_values else 0
        avg_hyg_detail = ScoreDetail(
            value=avg_hyg_val,
            label="Average",
            pros=list(hygiene_pros)[:5],
            cons=list(hygiene_cons)[:5]
        )
            
        # Analyze Personal README
        personal_readme_detail = self.profile_readme_analyzer.analyze(user_profile.readme_content or "")

        # 3. Prepare Context for LLM
        # We pass integer values to context builder for simplicity, or update it to use details. 
        # For now, passing integers is safer for existing prompt logic unless we update prompt.
        context = self._prepare_context(user_profile, tech_stack, avg_doc_val, personal_readme_detail.value, avg_hyg_val)

        # 4. Generate Analysis via LLM
        llm_result = self.llm_provider.generate_analysis(context)

        # 5. Map to AnalysisReport
        
        # Parse or wrap LLM scores into ScoreDetails (LLM returns ints usually)
        # We assume LLM returns simple ints for profile_score, repo_quality, overall.
        # We can wrap them in basic ScoreDetails for now.
        
        profile_score_val = int(llm_result.get("profile_score", 0))
        profile_score_detail = ScoreDetail(value=profile_score_val, label="AI Generated", pros=["Based on comprehensive analysis"], cons=[])
        
        repo_quality_val = int(llm_result.get("repo_quality_score", 0))
        repo_quality_detail = ScoreDetail(value=repo_quality_val, label="AI Generated", pros=[], cons=[])

        overall_val = int(llm_result.get("overall_score", 0))
        overall_detail = ScoreDetail(value=overall_val, label="AI Generated", pros=[], cons=[])

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
            profile_score=profile_score_detail,
            avg_repo_docs_score=avg_doc_detail,
            personal_readme_score=personal_readme_detail,
            avg_code_hygiene_score=avg_hyg_detail,
            repo_quality_score=repo_quality_detail,
            overall_score=overall_detail,
            summary=llm_result.get("summary", "Analysis complete."),
            suggestions=[Suggestion(**s) for s in llm_result.get("suggestions", [])],
            details=details,
            raw_llm_response=llm_result
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
            # repo.maturity_score is now a ScoreDetail object
            maturity_info = f"{repo.maturity_score.label} (Score: {repo.maturity_score.value})"
            
            hygiene_label_from_score = "Messy"
            # repo.code_hygiene_score is now a ScoreDetail object
            if repo.code_hygiene_score.value >= 80:
                hygiene_label_from_score = "Professional"
            elif repo.code_hygiene_score.value >= 60:
                hygiene_label_from_score = "Hygiene"
            elif repo.code_hygiene_score.value >= 40:
                hygiene_label_from_score = "Active"
            
            # Docs Details
            docs_label = "Weak"
            docs_missing = []
            # repo.repo_documentation_score is now a ScoreDetail object
            if repo.repo_documentation_score.value > 80:
                docs_label = "Strong"
            elif repo.repo_documentation_score.value > 50:
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
            
            docs_detail = f"{docs_label} (Score: {repo.repo_documentation_score.value})"
            if docs_missing:
                docs_detail += f" (Missing {', '.join(docs_missing)} section)"
            
            # 3. Explicit Signals (Ghost / Red Flags)
            prefix = ""
            
            # Ghost Project: Low maturity & inactive > 1 year
            if repo.maturity_score.value < 30 and days_since_update > 365:
                prefix = "[GHOST PROJECT] "
                status_str = "Ghost"

            # Final Line Construction
            line = (
                f"{prefix}Repo: {repo.name} | "
                f"Stack: {stack_str} | "
                f"Maturity: {maturity_info} | "
                f"Docs: {docs_detail} | "
                f"Hygiene: {hygiene_label_from_score} (Score: {repo.code_hygiene_score.value}) | "
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
