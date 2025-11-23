import re
from typing import List, Dict, Set, Tuple, Any
from datetime import datetime, timezone
from app.models.dtos import Repository, ScoreDetail

class ProfileReadmeAnalyzer:
    """
    Scores the user's personal profile README.
    """
    def analyze(self, content: str) -> ScoreDetail:
        score = 0
        positives = []
        negatives = []
        
        if not content:
            return ScoreDetail(score=0, level="Missing", negatives=["No README found"])
            
        lower_content = content.lower()
        
        # 1. Personal Branding Sections (+20 each)
        
        # "About Me" / "Introduction"
        if "about me" in lower_content or "introduction" in lower_content or "hi, i'm" in lower_content:
            score += 20
            positives.append("Includes 'About Me' / Introduction")
        else:
            negatives.append("Missing 'About Me' section")
            
        # "Tech Stack" / "Skills"
        if "tech stack" in lower_content or "skills" in lower_content or "technologies" in lower_content or "tools" in lower_content:
            score += 20
            positives.append("Lists Tech Stack / Skills")
        else:
            negatives.append("Missing Tech Stack / Skills section")
            
        # "Contact" / "Socials"
        if "contact" in lower_content or "social" in lower_content or "connect with me" in lower_content:
            score += 20
            positives.append("Includes Contact / Social links")
        else:
            negatives.append("Missing Contact / Socials section")
            
        # "Stats" / "Badges" (GitHub Stats images)
        if "github-readme-stats" in lower_content or "github-profile-trophy" in lower_content or "github-trophy" in lower_content or "streak-stats" in lower_content or "metrics" in lower_content:
            score += 20
            positives.append("Uses GitHub Stats / Badges")
        else:
            negatives.append("No GitHub Stats or Badges found")
            
        # 2. Length Bonus (+20)
        if len(content) > 500:
            score += 20
            positives.append("Detailed content (> 500 chars)")
        else:
            negatives.append("Content is brief (< 500 chars)")
            
        final_score = min(score, 100)
        level = "Strong" if final_score >= 80 else "Adequate" if final_score >= 40 else "Weak"
        
        return ScoreDetail(score=final_score, level=level, positives=positives, negatives=negatives)

class RepoDocumentationAnalyzer:
    """
    Scores the quality of a repository's documentation with multi-language support.
    """
    def analyze(self, repo: Repository) -> ScoreDetail:
        score = 0
        positives = []
        negatives = []
        
        readme = repo.readme_content or ""
        
        if not readme:
            return ScoreDetail(score=0, level="Missing", negatives=["No README found"])
        
        # Length Check
        if len(readme) > 500:
            score += 10
            positives.append("Detailed README content")
        else:
            negatives.append("Short README content")
            
        # Header Checks (Multi-language: English, Portuguese, Spanish)
        lower_readme = readme.lower()
        
        header_groups = {
            "Installation": ["installation", "instalação", "instalación", "setup", "configuração"],
            "Usage": ["usage", "uso", "utilização", "how to run", "como rodar"],
            "Getting Started": ["getting started", "começando", "primeiros passos", "empezando"],
            "API/Docs": ["api", "documentation", "documentação", "documentación", "docs"],
            "Contributing": ["contributing", "contribuição", "contribuyendo", "contribute"]
        }
        
        found_sections = []
        missing_sections = []
        
        for section_name, keywords in header_groups.items():
            if any(k in lower_readme for k in keywords):
                score += 10
                found_sections.append(section_name)
            else:
                missing_sections.append(section_name)
                
        if found_sections:
            positives.append(f"Contains sections: {', '.join(found_sections)}")
        if missing_sections:
            negatives.append(f"Missing sections: {', '.join(missing_sections)}")
        
        # Code Blocks Check
        if "```" in readme:
            score += 20
            positives.append("Includes code blocks/examples")
        else:
            negatives.append("No code blocks/examples found")
        
        final_score = min(score, 100)
        level = "Excellent" if final_score >= 80 else "Good" if final_score >= 50 else "Basic"
        
        return ScoreDetail(score=final_score, level=level, positives=positives, negatives=negatives)

class CommitHygieneAnalyzer:
    """
    Analyzes commit history for consistency and professional standards.
    """
    def analyze(self, history: List[Dict[str, Any]]) -> Tuple[ScoreDetail, float, float]:
        positives = []
        negatives = []
        
        if not history:
            return ScoreDetail(score=0, level="Inactive", negatives=["No commit history"]), 0.0, 0.0

        # 1. Calculate Metrics
        cc_pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+'
        cc_count = sum(1 for c in history if re.match(cc_pattern, c.get("message", "").strip()))
        cc_ratio = cc_count / len(history)
        
        dates = []
        for c in history:
            d_str = c.get("date")
            if d_str:
                try:
                    dates.append(datetime.fromisoformat(d_str.replace("Z", "+00:00")))
                except ValueError:
                    pass
        dates.sort()
        
        avg_days = 0.0
        if len(dates) >= 2:
            deltas = [(dates[i+1] - dates[i]).total_seconds() / 86400 for i in range(len(dates)-1)]
            avg_days = sum(deltas) / len(deltas) if deltas else 0.0
        
        total_len = sum(len(c.get("message", "")) for c in history)
        avg_msg_len = total_len / len(history) if history else 0

        # 2. Scoring Logic
        score = 0
        
        # Frequency (40pts)
        if avg_days < 7:
            score += 40
            positives.append("Excellent commit frequency (Active)")
        elif avg_days < 30:
            score += 20
            positives.append("Moderate commit frequency")
        else:
            negatives.append("Low commit frequency (> 30 days between commits)")
            
        # Message Length (30pts)
        if avg_msg_len > 15:
            score += 30
            positives.append("Descriptive commit messages")
        else:
            negatives.append("Commit messages are too short/vague")
            
        # Convention (30pts)
        score += int(cc_ratio * 30)
        if cc_ratio > 0.5:
            positives.append("Strong adherence to Conventional Commits")
        elif cc_ratio > 0.2:
            positives.append("Partial usage of Conventional Commits")
        else:
            negatives.append("Lack of Conventional Commits (feat:, fix:)")
        
        # 3. Classification
        level = "Standard"
        if score >= 80:
            level = "Professional"
        elif score >= 60:
            level = "Hygiene"
        elif score >= 40:
            level = "Active"
        elif avg_days > 60:
            level = "Inactive"
        else:
            level = "Standard"

        return ScoreDetail(score=score, level=level, positives=positives, negatives=negatives), cc_ratio, avg_days

class MaturityAnalyzer:
    """
    Calculates project maturity based on technical signals.
    """
    def analyze(self, repo: Repository) -> ScoreDetail:
        score = 0
        positives = []
        negatives = [] # These will act as recommendations

        # Technical signals
        if repo.has_ci:
            score += 20
            positives.append("CI/CD configured (GitHub Actions, etc.)")
        else:
            negatives.append("Add CI/CD pipelines (e.g., GitHub Actions)")
            
        if repo.has_tests:
            score += 20
            positives.append("Testing framework detected")
        else:
            negatives.append("Implement automated tests")
            
        if repo.has_docker:
            score += 10
            positives.append("Containerization (Docker) detected")
        else:
            negatives.append("Add Dockerfile for containerization")
            
        if repo.has_license:
            score += 10
            positives.append("License file present")
        else:
            negatives.append("Add a License file")
            
        # DevOps Synergy Bonus
        if repo.has_ci and repo.has_tests:
            score += 15
            positives.append("DevOps Synergy (CI + Tests)")
            
        # Description heuristic
        if repo.description:
            score += 5
            if len(repo.description) > 30:
                score += 5
                positives.append("Detailed repository description")
            if len(repo.description) > 100:
                score += 10
        else:
            negatives.append("Add a detailed repository description")
                
        # Conventional Commits
        if repo.conventional_commits_ratio > 0.5:
            score += 10
            positives.append("Consistent commit conventions")
        elif repo.conventional_commits_ratio > 0.2:
            score += 5
            
        # Ghost Project Penalty
        is_ghost = False
        try:
            last_update = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            if last_update.tzinfo is None:
                last_update = last_update.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if (now - last_update).days > 365:
                score -= 30
                is_ghost = True
                negatives.append("Revive or archive this project (inactive > 1 year)")
        except (ValueError, TypeError):
            pass
        
        score = max(0, min(score, 100))
        
        level = "Hobby"
        if is_ghost:
            level = "Archived/Ghost"
        elif score >= 75:
            level = "Production-Grade"
        elif score >= 45:
            level = "Prototype"
        else:
            level = "Hobby"
            
        return ScoreDetail(score=score, level=level, positives=positives, negatives=negatives)

class TechStackAnalyzer:
    """
    Identifies core vs experimental technologies based on usage and project maturity.
    """
    def analyze(self, repos: List[Repository]) -> Dict[str, List[str]]:
        production_repos = [r for r in repos if r.maturity_label == "Production-Grade"]
        hobby_repos = [r for r in repos if r.maturity_label == "Hobby"]
        
        # Helper to get stack items (Language + Dependencies)
        def get_stack_items(r: Repository) -> Set[str]:
            items = set()
            if r.language:
                items.add(r.language)
            # Add dependencies
            for dep in r.dependencies:
                 items.add(dep)
            return items

        # Count stack usage in production
        prod_counts: Dict[str, int] = {}
        for r in production_repos:
            for item in get_stack_items(r):
                prod_counts[item] = prod_counts.get(item, 0) + 1
                
        # Core Stack: Items in > 30% of production repos
        core_stack = []
        if production_repos:
            threshold = len(production_repos) * 0.3
            core_stack = [item for item, count in prod_counts.items() if count > threshold]
        
        # Experimentation: Items ONLY in hobby repos
        non_hobby_items = set()
        for r in repos:
            if r.maturity_label != "Hobby":
                non_hobby_items.update(get_stack_items(r))
                
        experimentation_stack = set()
        for r in hobby_repos:
            for item in get_stack_items(r):
                if item not in non_hobby_items:
                    experimentation_stack.add(item)
                
        return {
            "core_stack": sorted(list(core_stack)),
            "experimentation": sorted(list(experimentation_stack))
        }