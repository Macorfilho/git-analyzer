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
        from collections import Counter

        # 2. Run Insights (Maturity & Tech Stack)
        repo_docs_values = []
        all_repo_docs_pros = []
        all_repo_docs_cons = []
        
        hygiene_values = []
        all_hygiene_pros = []
        all_hygiene_cons = []
        
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
            repo.recommendations.extend(list(set(hygiene_detail.negatives))) # Add unique hygiene gaps
            
            hygiene_values.append(hygiene_detail.score)
            all_hygiene_pros.extend(hygiene_detail.positives)
            all_hygiene_cons.extend(hygiene_detail.negatives)
            
            # Repo Documentation
            doc_detail = self.repo_doc_analyzer.analyze(repo)
            repo.repo_documentation_score = doc_detail
            
            repo_docs_values.append(doc_detail.score)
            all_repo_docs_pros.extend(doc_detail.positives)
            all_repo_docs_cons.extend(doc_detail.negatives)
            
            # Maturity
            maturity_detail = self.maturity_analyzer.analyze(repo)
            repo.maturity_score = maturity_detail
            repo.maturity_label = maturity_detail.level
            repo.recommendations.extend(list(set(maturity_detail.negatives))) # Add unique maturity gaps
            
        tech_stack = self.tech_stack_analyzer.analyze(user_profile.repositories)
        
        # Helper to aggregate feedback smartly
        def aggregate_feedback(pros_list, cons_list, total_repos):
            final_pros = []
            final_cons = []
            
            pros_counts = Counter(pros_list)
            cons_counts = Counter(cons_list)
            
            # Threshold: trait must appear in > 40% of repos to be "dominant"
            threshold = total_repos * 0.4 if total_repos > 0 else 0
            
            dominant_pros = {k for k, v in pros_counts.items() if v > threshold}
            dominant_cons = {k for k, v in cons_counts.items() if v > threshold}
            
            # Conflict Resolution
            # Hygiene Conflicts
            if "Excellent commit frequency (Active)" in dominant_pros and "Low commit frequency (> 30 days between commits)" in dominant_cons:
                final_cons.append("Inconsistent commit frequency across repositories")
                dominant_pros.discard("Excellent commit frequency (Active)")
                dominant_cons.discard("Low commit frequency (> 30 days between commits)")
            
            if "Descriptive commit messages" in dominant_pros and "Commit messages are too short/vague" in dominant_cons:
                final_cons.append("Inconsistent commit message quality")
                dominant_pros.discard("Descriptive commit messages")
                dominant_cons.discard("Commit messages are too short/vague")

            # Docs Conflicts
            if "Detailed README content" in dominant_pros and "Short README content" in dominant_cons:
                final_cons.append("Inconsistent documentation depth")
                dominant_pros.discard("Detailed README content")
                dominant_cons.discard("Short README content")

            final_pros.extend(list(dominant_pros))
            final_cons.extend(list(dominant_cons))
            
            # Fallback: Ensure we show negatives if they exist but were filtered out
            if not final_cons and cons_counts:
                 final_cons.extend([k for k, v in cons_counts.most_common(3)])
            
            return final_pros[:5], final_cons[:5]

        total_repos = len(user_profile.repositories)
        
        # Aggregates for AnalysisReport
        
        # Avg Repo Docs
        avg_doc_val = int(sum(repo_docs_values) / len(repo_docs_values)) if repo_docs_values else 0
        agg_doc_pros, agg_doc_cons = aggregate_feedback(all_repo_docs_pros, all_repo_docs_cons, total_repos)
        
        avg_doc_detail = ScoreDetail(
            score=avg_doc_val,
            level="Average",
            positives=agg_doc_pros,
            negatives=agg_doc_cons
        )
        
        # Avg Hygiene
        avg_hyg_val = int(sum(hygiene_values) / len(hygiene_values)) if hygiene_values else 0
        agg_hyg_pros, agg_hyg_cons = aggregate_feedback(all_hygiene_pros, all_hygiene_cons, total_repos)
        
        avg_hyg_detail = ScoreDetail(
            score=avg_hyg_val,
            level="Average",
            positives=agg_hyg_pros,
            negatives=agg_hyg_cons
        )
            
        # Analyze Personal README
        personal_readme_detail = self.profile_readme_analyzer.analyze(user_profile.readme_content or "")

        # 3. Prepare Context for LLM
        context = self._prepare_context(user_profile, tech_stack, avg_doc_val, personal_readme_detail.score, avg_hyg_val)

        # 4. Generate Analysis via LLM
        llm_result = self.llm_provider.generate_analysis(context)

        # 5. Map to AnalysisReport
        
        # Parse or wrap LLM scores into ScoreDetails (LLM returns ints usually)
        # We assume LLM returns simple ints for profile_score, repo_quality, overall.
        # We can wrap them in basic ScoreDetails for now.
        
        profile_score_val = int(llm_result.get("profile_score", 0))
        profile_score_detail = ScoreDetail(score=profile_score_val, level="AI Generated", positives=["Based on comprehensive analysis"], negatives=[])
        
        repo_quality_val = int(llm_result.get("repo_quality_score", 0))
        repo_quality_detail = ScoreDetail(score=repo_quality_val, level="AI Generated", positives=[], negatives=[])

        overall_val = int(llm_result.get("overall_score", 0))
        overall_detail = ScoreDetail(score=overall_val, level="AI Generated", positives=[], negatives=[])

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
            maturity_info = f"{repo.maturity_score.level} (Score: {repo.maturity_score.score})"
            
            hygiene_label_from_score = "Messy"
            # repo.code_hygiene_score is now a ScoreDetail object
            if repo.code_hygiene_score.score >= 80:
                hygiene_label_from_score = "Professional"
            elif repo.code_hygiene_score.score >= 60:
                hygiene_label_from_score = "Hygiene"
            elif repo.code_hygiene_score.score >= 40:
                hygiene_label_from_score = "Active"
            
            # Docs Details
            docs_label = "Weak"
            docs_missing = []
            # repo.repo_documentation_score is now a ScoreDetail object
            if repo.repo_documentation_score.score > 80:
                docs_label = "Strong"
            elif repo.repo_documentation_score.score > 50:
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
            
            docs_detail = f"{docs_label} (Score: {repo.repo_documentation_score.score})"
            if docs_missing:
                docs_detail += f" (Missing {', '.join(docs_missing)} section)"
            
            # 3. Explicit Signals (Ghost / Red Flags)
            prefix = ""
            
            # Ghost Project: Low maturity & inactive > 1 year
            if repo.maturity_score.score < 30 and days_since_update > 365:
                prefix = "[GHOST PROJECT] "
                status_str = "Ghost"

            # Final Line Construction
            line = (
                f"{prefix}Repo: {repo.name} | "
                f"Stack: {stack_str} | "
                f"Maturity: {maturity_info} | "
                f"Docs: {docs_detail} | "
                f"Hygiene: {hygiene_label_from_score} (Score: {repo.code_hygiene_score.score}) | "
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
