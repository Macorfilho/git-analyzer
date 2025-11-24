import unittest
from app.models.dtos import Repository
from app.services.insight_engine import MaturityAnalyzer, RepoDocumentationAnalyzer

class TestNewLogic(unittest.TestCase):

    def test_maturity_academic(self):
        analyzer = MaturityAnalyzer()
        # Academic keyword in description
        repo = Repository(
            name="my-course-work",
            description="This is a study project for a bootcamp",
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com",
            file_tree=["a", "b", "c", "d"] # not utility
        )
        result = analyzer.analyze(repo)
        self.assertEqual(result.level, "Academic")

        # Academic keyword in name
        repo2 = Repository(
            name="python-study-guide",
            description="Some code",
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com",
            file_tree=["a", "b", "c", "d"]
        )
        result2 = analyzer.analyze(repo2)
        self.assertEqual(result2.level, "Academic")

    def test_maturity_utility(self):
        analyzer = MaturityAnalyzer()
        # Small file tree (< 4) and has readme
        repo = Repository(
            name="util-script",
            description="Just a script",
            readme_content="# Readme",
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com",
            file_tree=["script.py", "README.md", "requirements.txt"] # 3 files
        )
        result = analyzer.analyze(repo)
        self.assertEqual(result.level, "Utility")
        
        # No readme -> Hobby (or whatever score dictates, but check utility condition)
        # Code requires readme_content for utility
        repo_no_readme = Repository(
            name="util-script-no-readme",
            description="Just a script",
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com",
            file_tree=["script.py"]
        )
        result_no_readme = analyzer.analyze(repo_no_readme)
        self.assertNotEqual(result_no_readme.level, "Utility")

    def test_maturity_downgrade(self):
        analyzer = MaturityAnalyzer()
        # High score (CI + Tests + Docker + License = 60, + conventional commits maybe)
        # Let's force a high score manually or by setting attributes
        repo = Repository(
            name="production-app",
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com",
            has_ci=True,
            has_tests=True, # +15 synergy
            has_docker=True,
            has_license=True,
            conventional_commits_ratio=0.6, # +10
            file_tree=["a"]*10 # ensure not utility
        )
        # Total score estimation: 
        # CI (20) + Tests (20) + Docker (10) + License (10) + Synergy (15) + CC (10) = 85
        # Should be Production-Grade
        
        # But missing description AND readme -> Downgrade to Prototype
        # Wait, code says "if not repo.description OR not repo.readme_content"
        # So if either is missing, downgrade.
        
        result = analyzer.analyze(repo)
        self.assertEqual(result.level, "Prototype")
        self.assertIn("Downgraded to Prototype due to missing description/README", result.negatives)
        
        # Now add description and readme
        repo.description = "A robust production application."
        repo.readme_content = "# Readme"
        result_ok = analyzer.analyze(repo)
        self.assertEqual(result_ok.level, "Production-Grade")

    def test_repo_docs_multilingual_usage(self):
        analyzer = RepoDocumentationAnalyzer()
        repo = Repository(
            name="pt-repo",
            readme_content="# Como usar\nExecute o script.",
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com"
        )
        result = analyzer.analyze(repo)
        self.assertIn("Contains sections: Usage", result.positives)

if __name__ == "__main__":
    unittest.main()
