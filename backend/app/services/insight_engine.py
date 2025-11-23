import re
from typing import List, Dict, Set, Tuple, Any
from datetime import datetime, timezone
from app.models.dtos import Repository

class ProfileReadmeAnalyzer:
    """
    Scores the user's personal profile README.
    """
    def analyze(self, content: str) -> int:
        score = 0
        if not content:
            return 0
            
        lower_content = content.lower()
        
        # 1. Personal Branding Sections (+20 each)
        
        # "About Me" / "Introduction"
        if "about me" in lower_content or "introduction" in lower_content or "hi, i'm" in lower_content:
            score += 20
            
        # "Tech Stack" / "Skills"
        if "tech stack" in lower_content or "skills" in lower_content or "technologies" in lower_content or "tools" in lower_content:
            score += 20
            
        # "Contact" / "Socials"
        if "contact" in lower_content or "social" in lower_content or "connect with me" in lower_content:
            score += 20
            
        # "Stats" / "Badges" (GitHub Stats images)
        # Look for common stats card URLs or markdown image syntax generally in a stats context
        if "github-readme-stats" in lower_content or "github-profile-trophy" in lower_content or "github-trophy" in lower_content or "streak-stats" in lower_content or "metrics" in lower_content:
            score += 20
            
        # 2. Length Bonus (+20)
        if len(content) > 500:
            score += 20
            
        return min(score, 100)

class RepoDocumentationAnalyzer:
    """
    Scores the quality of a repository's documentation.
    """
    def analyze(self, repo: Repository) -> int:
        score = 0
        readme = repo.readme_content or ""
        
        if not readme:
            return 0
        
        # Length Check: +10 if detailed (> 500 chars)
        if len(readme) > 500:
            score += 10
            
        # Header Checks (Case Insensitive)
        # +10 points per header type found
        lower_readme = readme.lower()
        target_headers = ["installation", "usage", "getting started", "api", "contributing"]
        found_headers = set()
        for h in target_headers:
            if h in lower_readme:
                found_headers.add(h)
        score += (len(found_headers) * 10)
        
        # Code Blocks Check: +20 points
        if "```" in readme:
            score += 20
        
        return min(score, 100)

class CommitHygieneAnalyzer:
    """
    Analyzes commit history for consistency and professional standards.
    """
    def analyze(self, history: List[Dict[str, Any]]) -> Tuple[str, float, float, int]:
        if not history:
            return "Inactive", 0.0, 0.0

        # 1. Calculate Metrics
        
        # Conventional Commits Ratio
        cc_pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+'
        cc_count = sum(1 for c in history if re.match(cc_pattern, c.get("message", "").strip()))
        cc_ratio = cc_count / len(history)
        
        # Commit Frequency (Average days between commits)
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
        elif len(dates) == 1:
            # If only one commit, treat it as reasonably active but with 0 interval
            avg_days = 0.0 

        # Message Length
        total_len = sum(len(c.get("message", "")) for c in history)
        avg_msg_len = total_len / len(history) if history else 0

        # 2. Scoring Logic (Weighted Sum 0-100)
        score = 0
        
        # Frequency (40pts)
        if avg_days < 7:
            score += 40
        elif avg_days < 30:
            score += 20
        else:
            score += 0
            
        # Message Length (30pts)
        if avg_msg_len > 15:
            score += 30
            
        # Convention (30pts)
        score += (cc_ratio * 30)
        
        # 3. Classification based on Score
        label = "Standard"
        if score >= 80:
            label = "Professional" # High hygiene + activity
        elif score >= 60:
            label = "Hygiene"      # Good practices
        elif score >= 40:
            label = "Active"       # Active but maybe messy
        elif avg_days > 60:
            label = "Inactive"
        else:
            label = "Standard"     # Middle ground

        return label, cc_ratio, avg_days, score

class MaturityAnalyzer:
    """
    Calculates project maturity based on technical signals.
    """
    def analyze(self, repo: Repository) -> tuple[int, str]:
        score = 0
        label = "Hobby"

        # Technical signals
        if repo.has_ci:
            score += 20
        if repo.has_tests:
            score += 20
        if repo.has_docker:
            score += 10
        if repo.has_license:
            score += 10
            
        # DevOps Synergy Bonus
        if repo.has_ci and repo.has_tests:
            score += 15
            
        # Description heuristic
        if repo.description:
            score += 5
            if len(repo.description) > 30:
                score += 5
            if len(repo.description) > 100:
                score += 10
                
        # Conventional Commits (New)
        if repo.conventional_commits_ratio > 0.5:
            score += 10
        elif repo.conventional_commits_ratio > 0.2:
            score += 5
            
        # Ghost Project Penalty (Last update > 1 year)
        is_ghost = False
        try:
            # Handle timezone info roughly
            last_update = datetime.fromisoformat(repo.updated_at.replace("Z", "+00:00"))
            # If repo.updated_at has no tz, assume UTC
            if last_update.tzinfo is None:
                last_update = last_update.replace(tzinfo=timezone.utc)
                
            now = datetime.now(timezone.utc)
            if (now - last_update).days > 365:
                score -= 30
                is_ghost = True
        except (ValueError, TypeError):
            pass
        
        # Cap score
        score = max(0, min(score, 100))
        
        # Classification
        if is_ghost:
            label = "Archived/Ghost"
        elif score >= 75: # Slightly higher threshold for top tier
            label = "Production-Grade"
        elif score >= 45:
            label = "Prototype"
        else:
            label = "Hobby"
            
        return score, label

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
