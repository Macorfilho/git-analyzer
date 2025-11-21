from typing import List, Dict, Set
from app.models.dtos import Repository

class MaturityAnalyzer:
    """
    Calculates project maturity based on technical signals.
    """
    def analyze(self, repo: Repository) -> tuple[int, str]:
        score = 0
        
        # Technical signals
        if repo.has_ci:
            score += 20
        if repo.has_tests:
            score += 20
        if repo.has_docker:
            score += 10
        if repo.has_license:
            score += 10
            
        # Description heuristic
        if repo.description:
            score += 10
            if len(repo.description) > 30:
                score += 10
            if len(repo.description) > 100:
                score += 20
        
        # Cap score at 100
        score = min(score, 100)
        
        # Classification
        if score >= 70:
            label = "Production-Grade"
        elif score >= 40:
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
        
        # Count languages in production repos
        prod_langs: Dict[str, int] = {}
        for r in production_repos:
            if r.language:
                prod_langs[r.language] = prod_langs.get(r.language, 0) + 1
                
        # Core Stack: Languages in > 50% of production repos
        core_stack = []
        if production_repos:
            threshold = len(production_repos) * 0.5
            core_stack = [lang for lang, count in prod_langs.items() if count > threshold]
        
        # Experimentation: Languages ONLY in hobby repos
        # First get all languages used in non-hobby repos (Production + Prototype)
        non_hobby_langs = set()
        for r in repos:
            if r.maturity_label != "Hobby" and r.language:
                non_hobby_langs.add(r.language)
                
        experimentation_stack = set()
        for r in hobby_repos:
            if r.language and r.language not in non_hobby_langs:
                experimentation_stack.add(r.language)
                
        return {
            "core_stack": sorted(list(core_stack)),
            "experimentation": sorted(list(experimentation_stack))
        }
