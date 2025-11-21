import unittest
from app.services.collectors import StructureCollector, DependencyCollector

class TestCollectors(unittest.TestCase):
    def test_structure_collector_deep_mining(self):
        collector = StructureCollector()
        
        files = [
            "README.md",
            "src/main.py",
            "src/tests/test_main.py", # Should trigger tests
            ".github/workflows/ci.yml", # Should trigger CI
            "deploy/Dockerfile", # Should trigger Docker
            "LICENSE" # Should trigger License
        ]
        
        flags = collector.analyze(files)
        
        self.assertTrue(flags["has_tests"], "Should detect tests in deep folder")
        self.assertTrue(flags["has_ci"], "Should detect CI in .github")
        self.assertTrue(flags["has_docker"], "Should detect Dockerfile deep in tree")
        self.assertTrue(flags["has_license"], "Should detect License")

    def test_structure_collector_signals(self):
        collector = StructureCollector()
        # Case 2: Other signals
        files = [
            "spec/my_spec.rb", # Tests
            ".gitlab-ci.yml", # CI
            "docker-compose.yml" # Docker
        ]
        flags = collector.analyze(files)
        self.assertTrue(flags["has_tests"])
        self.assertTrue(flags["has_ci"])
        self.assertTrue(flags["has_docker"])

    def test_dependency_collector_pyproject(self):
        collector = DependencyCollector()
        
        dependency_files = {
            "pyproject.toml": """
[tool.poetry.dependencies]
python = "^3.9"
flask = "^2.0"
requests = "^2.26"

[tool.poetry.dev-dependencies]
pytest = "^6.2"
"""
        }
            
        deps = collector.analyze(dependency_files)
        self.assertIn("flask", deps)
        self.assertIn("requests", deps)
        self.assertIn("python", deps) 

    def test_dependency_collector_composer(self):
        collector = DependencyCollector()
        
        dependency_files = {
            "composer.json": """
{
    "require": {
        "php": "^8.0",
        "monolog/monolog": "^2.0",
        "guzzlehttp/guzzle": "^7.0"
    }
}
"""
        }
            
        deps = collector.analyze(dependency_files)
        self.assertIn("monolog/monolog", deps)
        self.assertIn("guzzlehttp/guzzle", deps)
        self.assertNotIn("php", deps)

if __name__ == "__main__":
    unittest.main()