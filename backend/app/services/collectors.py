from typing import List, Callable, Optional, Any, Dict
import json
import re

class StructureCollector:
    """
    Analyzes the file structure of a repository to detect key characteristics.
    """
    def analyze(self, root_files: List[str]) -> Dict[str, bool]:
        flags = {
            "has_ci": False,
            "has_docker": False,
            "has_tests": False,
            "has_license": False
        }
        
        normalized_files = [f.lower() for f in root_files]
        
        # Check for CI (GitHub Actions, Travis)
        # Note: Existence of .github implies potentially Actions, but strictly we should check workflows.
        # Given we only have root files here, we use .github as a proxy or look for specific CI files.
        if ".github" in normalized_files or ".travis.yml" in normalized_files:
             flags["has_ci"] = True
             
        # Check for Docker
        if any("dockerfile" in f for f in normalized_files):
            flags["has_docker"] = True
            
        # Check for Tests (common folders or config files)
        if any(f in ["tests", "test", "spec", "__tests__"] for f in normalized_files) or "pytest.ini" in normalized_files:
            flags["has_tests"] = True
            
        # Check for License
        if any("license" in f for f in normalized_files) or "copying" in normalized_files:
            flags["has_license"] = True
            
        return flags

class DependencyCollector:
    """
    Extracts dependency information from package manifest files.
    """
    def analyze(self, repo_obj: Any, fetch_content_func: Callable[[Any, str], Optional[str]]) -> List[str]:
        dependencies = set()
        
        # Strategy: Try to fetch common dependency files and parse them.
        
        # 1. Python (requirements.txt)
        req_txt = fetch_content_func(repo_obj, "requirements.txt")
        if req_txt:
            for line in req_txt.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Regex to capture package name at start of line, ignoring version specifiers
                    # e.g. "flask==2.0.1" -> "flask"
                    # e.g. "requests>=2.0" -> "requests"
                    match = re.match(r'^([a-zA-Z0-9\-_]+)', line)
                    if match:
                        dependencies.add(match.group(1))

        # 2. Node.js (package.json)
        pkg_json = fetch_content_func(repo_obj, "package.json")
        if pkg_json:
            try:
                data = json.loads(pkg_json)
                deps = data.get('dependencies', {})
                dev_deps = data.get('devDependencies', {})
                if isinstance(deps, dict):
                    dependencies.update(deps.keys())
                if isinstance(dev_deps, dict):
                    dependencies.update(dev_deps.keys())
            except json.JSONDecodeError:
                pass
        
        # Limit to reasonable number to avoid clutter
        return sorted(list(dependencies))[:30]
