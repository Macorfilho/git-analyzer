from typing import List, Dict, Any
import json
import re
from datetime import datetime

class StructureCollector:
    """
    Analyzes the file structure of a repository to detect key characteristics.
    """
    def analyze(self, file_paths: List[str]) -> Dict[str, bool]:
        flags = {
            "has_ci": False,
            "has_docker": False,
            "has_tests": False,
            "has_license": False
        }
        
        # Convert all paths to lowercase for case-insensitive matching
        normalized_files = [f.lower() for f in file_paths]
        
        for f in normalized_files:
            # Check for CI
            if ".github/workflows" in f or ".gitlab-ci.yml" in f or "circleci/" in f or ".circleci/" in f or ".travis.yml" in f:
                flags["has_ci"] = True
            
            # Check for Docker
            if "dockerfile" in f or "docker-compose" in f:
                flags["has_docker"] = True
            
            # Check for Tests
            parts = f.split('/')
            if any(p in ["test", "tests", "spec", "__tests__"] for p in parts):
                flags["has_tests"] = True
            elif f.endswith(("_test.py", ".test.js", "_spec.rb", "pytest.ini")):
                flags["has_tests"] = True
                
            # Check for License
            if "license" in f or "copying" in f:
                flags["has_license"] = True
                
        return flags

class DependencyCollector:
    """
    Extracts dependency information from package manifest files.
    """
    def analyze(self, dependency_files: Dict[str, str]) -> List[str]:
        dependencies = set()
        
        # 1. Python (requirements.txt)
        req_txt = dependency_files.get("requirements.txt")
        if req_txt:
            for line in req_txt.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    match = re.match(r'^([a-zA-Z0-9\-_]+)', line)
                    if match:
                        dependencies.add(match.group(1))

        # Python (pyproject.toml)
        pyproject = dependency_files.get("pyproject.toml")
        if pyproject:
            in_deps = False
            for line in pyproject.split('\n'):
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    if "dependencies" in line and ("tool.poetry" in line or "project" in line):
                        in_deps = True
                    else:
                        in_deps = False
                    continue
                
                if in_deps and line and not line.startswith("#"):
                    match = re.match(r'^([a-zA-Z0-9\-_]+)\s*=', line)
                    if match:
                         dependencies.add(match.group(1))

        # 2. Node.js (package.json)
        pkg_json = dependency_files.get("package.json")
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

        # 3. Go (go.mod)
        go_mod = dependency_files.get("go.mod")
        if go_mod:
             # Look for packages in require (...) or direct lines
             # Matches lines like: "github.com/pkg/errors v0.9.1" or indented inside require
             # Also matches "require google.golang.org/grpc v1.40.0"
             matches = re.findall(r'^\s*(?:require\s+)?([a-zA-Z0-9\.\-/]+)\s+v[0-9]', go_mod, re.MULTILINE)
             dependencies.update(matches)

        # 4. Rust (Cargo.toml)
        cargo_toml = dependency_files.get("Cargo.toml")
        if cargo_toml:
            in_deps = False
            for line in cargo_toml.split('\n'):
                line = line.strip()
                if line == "[dependencies]":
                    in_deps = True
                    continue
                if line.startswith("[") and line != "[dependencies]":
                    in_deps = False
                
                if in_deps and line and not line.startswith("#"):
                     # Match: name = "version" or name = { version = "..." }
                     match = re.match(r'^([a-zA-Z0-9\-_]+)\s*=', line)
                     if match:
                         dependencies.add(match.group(1))

        # 5. Java (pom.xml)
        pom_xml = dependency_files.get("pom.xml")
        if pom_xml:
            matches = re.findall(r'<artifactId>([a-zA-Z0-9\.\-_]+)</artifactId>', pom_xml)
            dependencies.update(matches)
            
        # 6. Java/Kotlin (build.gradle)
        build_gradle = dependency_files.get("build.gradle")
        if build_gradle:
            # Match: implementation 'group:name:version' or implementation("...")
            matches = re.findall(r'implementation\s*\(?[\'"]([^\'"]+)[\'"]', build_gradle)
            # Clean up matches (sometimes they include group:)
            for m in matches:
                if ':' in m:
                    dependencies.add(m.split(':')[1]) # Add artifactId only usually, or full? Let's add full for now or artifact. 
                    # pom.xml adds artifactId. Let's stick to artifactId if possible or just the full string.
                    # The user requirement doesn't specify. Let's keep full string or split.
                    # pom.xml logic: <artifactId>...
                    # build.gradle: "com.example:lib:1.0" -> "lib"?
                    # Let's try to extract the name.
                    dependencies.add(m)
                else:
                    dependencies.add(m)

        # 7. PHP (composer.json)
        composer = dependency_files.get("composer.json")
        if composer:
            try:
                # Try JSON parse first
                data = json.loads(composer)
                deps = data.get('require', {})
                if isinstance(deps, dict):
                    dependencies.update([k for k in deps.keys() if k.lower() != 'php'])
            except json.JSONDecodeError:
                # Fallback to regex if JSON fails (as per "regex support" hint)
                matches = re.findall(r'"([a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+)"\s*:', composer)
                dependencies.update(matches)
        
        return sorted(list(dependencies))[:30]

class GitHistoryCollector:
    """
    Analyzes commit history to extract development patterns.
    Deprecated: Use CommitHygieneAnalyzer in insight_engine.py
    """
    def analyze(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not history:
            return {
                "commit_frequency": 0.0,
                "conventional_commits_ratio": 0.0,
                "average_message_length": 0.0
            }
        
        total_len = sum(len(c.get("message", "")) for c in history)
        avg_len = total_len / len(history)
        
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
        
        freq = 0.0
        if len(dates) >= 2:
            dates.sort()
            delta = dates[-1] - dates[0]
            days = delta.total_seconds() / 86400
            if days > 0:
                freq = len(dates) / days
            else:
                freq = float(len(dates))
        elif len(dates) == 1:
            freq = 1.0
            
        return {
            "commit_frequency": round(freq, 2),
            "conventional_commits_ratio": round(cc_ratio, 2),
            "average_message_length": round(avg_len, 1)
        }
