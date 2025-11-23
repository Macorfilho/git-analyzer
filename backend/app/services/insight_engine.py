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
        pros = []
        cons = []
        
        if not content:
            return ScoreDetail(value=0, label="Missing", cons=["No README found"])
            
        lower_content = content.lower()
        
        # 1. Personal Branding Sections (+20 each)
        
        # "About Me" / "Introduction"
        if "about me" in lower_content or "introduction" in lower_content or "hi, i'm" in lower_content:
            score += 20
            pros.append("Includes 'About Me' / Introduction")
        else:
            cons.append("Missing 'About Me' section")
            
        # "Tech Stack" / "Skills"
        if "tech stack" in lower_content or "skills" in lower_content or "technologies" in lower_content or "tools" in lower_content:
            score += 20
            pros.append("Lists Tech Stack / Skills")
        else:
            cons.append("Missing Tech Stack / Skills section")
            
        # "Contact" / "Socials"
        if "contact" in lower_content or "social" in lower_content or "connect with me" in lower_content:
            score += 20
            pros.append("Includes Contact / Social links")
        else:
            cons.append("Missing Contact / Socials section")
            
        # "Stats" / "Badges" (GitHub Stats images)
        if "github-readme-stats" in lower_content or "github-profile-trophy" in lower_content or "github-trophy" in lower_content or "streak-stats" in lower_content or "metrics" in lower_content:
            score += 20
            pros.append("Uses GitHub Stats / Badges")
        else:
            cons.append("No GitHub Stats or Badges found")
            
        # 2. Length Bonus (+20)
        if len(content) > 500:
            score += 20
            pros.append("Detailed content (> 500 chars)")
        else:
            cons.append("Content is brief (< 500 chars)")
            
        final_score = min(score, 100)
        label = "Strong" if final_score >= 80 else "Adequate" if final_score >= 40 else "Weak"
        
        return ScoreDetail(value=final_score, label=label, pros=pros, cons=cons)

class RepoDocumentationAnalyzer:
    """
    Scores the quality of a repository's documentation.
    """
    def analyze(self, repo: Repository) -> ScoreDetail:
        score = 0
        pros = []
        cons = []
        
        readme = repo.readme_content or ""
        
        if not readme:
            return ScoreDetail(value=0, label="Missing", cons=["No README found"])
        
        # Length Check
        if len(readme) > 500:
            score += 10
            pros.append("Detailed README content")
        else:
            cons.append("Short README content")
            
        # Header Checks (Case Insensitive)
        lower_readme = readme.lower()
        target_headers = ["installation", "usage", "getting started", "api", "contributing"]
        found_headers = []
        missing_headers = []
        
        for h in target_headers:
            if h in lower_readme:
                found_headers.append(h.title())
            else:
                missing_headers.append(h.title())
                
        score += (len(found_headers) * 10)
        if found_headers:
            pros.append(f"Contains sections: {', '.join(found_headers)}")
        if missing_headers:
            cons.append(f"Missing sections: {', '.join(missing_headers)}")
        
        # Code Blocks Check
        if "```" in readme:
            score += 20
            pros.append("Includes code blocks/examples")
        else:
            cons.append("No code blocks/examples found")
        
        final_score = min(score, 100)
        label = "Excellent" if final_score >= 80 else "Good" if final_score >= 50 else "Basic"
        
        return ScoreDetail(value=final_score, label=label, pros=pros, cons=cons)

class CommitHygieneAnalyzer:
    """
    Analyzes commit history for consistency and professional standards.
    """
    def analyze(self, history: List[Dict[str, Any]]) -> Tuple[ScoreDetail, float, float]:
        # Returns (ScoreDetail, cc_ratio, avg_days) - maintaining tuple for backward compat in service unpacking if needed, 
        # but ScoreDetail encapsulates the score.
        
        pros = []
        cons = []
        
        if not history:
            return ScoreDetail(value=0, label="Inactive", cons=["No commit history"]), 0.0, 0.0

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
            pros.append("High commit frequency (< 7 days)")
        elif avg_days < 30:
            score += 20
            pros.append("Moderate commit frequency (< 30 days)")
        else:
            cons.append("Low commit frequency (> 30 days)")
            
        # Message Length (30pts)
        if avg_msg_len > 15:
            score += 30
            pros.append("Good commit message length")
        else:
            cons.append("Commit messages are too short")
            
        # Convention (30pts)
        score += int(cc_ratio * 30)
        if cc_ratio > 0.5:
            pros.append("High usage of Conventional Commits")
        elif cc_ratio > 0.2:
            pros.append("Some usage of Conventional Commits")
        else:
            cons.append("Low usage of Conventional Commits")
        
        # 3. Classification
        label = "Standard"
        if score >= 80:
            label = "Professional"
        elif score >= 60:
            label = "Hygiene"
        elif score >= 40:
            label = "Active"
        elif avg_days > 60:
            label = "Inactive"
        else:
            label = "Standard"

        return ScoreDetail(value=score, label=label, pros=pros, cons=cons), cc_ratio, avg_days

class MaturityAnalyzer:
    """
    Calculates project maturity based on technical signals.
    """
    def analyze(self, repo: Repository) -> ScoreDetail:
        score = 0
        pros = []
        cons = [] # These will act as recommendations

        # Technical signals
        if repo.has_ci:
            score += 20
            pros.append("CI/CD configured")
        else:
            cons.append("Missing CI/CD configuration")
            
        if repo.has_tests:
            score += 20
            pros.append("Tests detected")
        else:
            cons.append("No tests detected")
            
        if repo.has_docker:
            score += 10
            pros.append("Containerization (Docker) detected")
        else:
            cons.append("No Docker/Containerization")
            
        if repo.has_license:
            score += 10
            pros.append("License file present")
        else:
            cons.append("Missing License")
            
        # DevOps Synergy Bonus
        if repo.has_ci and repo.has_tests:
            score += 15
            pros.append("DevOps Synergy (CI + Tests)")
            
        # Description heuristic
        if repo.description:
            score += 5
            if len(repo.description) > 30:
                score += 5
                pros.append("Detailed description")
            if len(repo.description) > 100:
                score += 10
        else:
            cons.append("Missing repository description")
                
        # Conventional Commits
        if repo.conventional_commits_ratio > 0.5:
            score += 10
            pros.append("Consistent commit conventions")
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
                cons.append("Repository is inactive (> 1 year)")
        except (ValueError, TypeError):
            pass
        
        score = max(0, min(score, 100))
        
        label = "Hobby"
        if is_ghost:
            label = "Archived/Ghost"
        elif score >= 75:
            label = "Production-Grade"
        elif score >= 45:
            label = "Prototype"
        else:
            label = "Hobby"
            
        return ScoreDetail(value=score, label=label, pros=pros, cons=cons)

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
