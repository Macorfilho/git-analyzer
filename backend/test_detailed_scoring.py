import unittest
from app.services.insight_engine import ProfileReadmeAnalyzer, RepoDocumentationAnalyzer, CommitHygieneAnalyzer, MaturityAnalyzer
from app.models.dtos import Repository

class TestDetailedScoring(unittest.TestCase):
    def test_profile_readme_details(self):
        analyzer = ProfileReadmeAnalyzer()
        # Empty
        res = analyzer.analyze("")
        self.assertEqual(res.value, 0)
        self.assertIn("No README found", res.cons)
        
        # Rich content
        content = "# About Me\nHi.\n# Tech Stack\nPython.\n# Contact\nEmail.\n" + "a"*501
        res = analyzer.analyze(content)
        self.assertEqual(res.value, 80) # 20+20+20+20 (length) = 80. Missing stats.
        self.assertIn("Includes 'About Me' / Introduction", res.pros)
        self.assertIn("Detailed content (> 500 chars)", res.pros)
        self.assertIn("No GitHub Stats or Badges found", res.cons)
        
    def test_repo_docs_details(self):
        analyzer = RepoDocumentationAnalyzer()
        repo = Repository(
            name="test", 
            readme_content="# Installation\nRun it.\n```\ncode\n```",
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com"
        )
        res = analyzer.analyze(repo)
        self.assertTrue(res.value >= 30) # 10 (install) + 20 (code) = 30. Short length.
        self.assertIn("Contains sections: Installation", res.pros)
        self.assertIn("Includes code blocks/examples", res.pros)
        self.assertIn("Short README content", res.cons)
        
    def test_maturity_details(self):
        analyzer = MaturityAnalyzer()
        repo = Repository(
            name="test", 
            has_ci=True, 
            has_tests=False, 
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com"
        )
        res = analyzer.analyze(repo)
        self.assertIn("CI/CD configured", res.pros)
        self.assertIn("No tests detected", res.cons)
        self.assertIn("Missing License", res.cons)

if __name__ == "__main__":
    unittest.main()

