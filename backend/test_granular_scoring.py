import unittest
from app.models.dtos import ScoreDetail, Repository
from app.services.insight_engine import ProfileReadmeAnalyzer, RepoDocumentationAnalyzer, CommitHygieneAnalyzer, MaturityAnalyzer

class TestGranularScoring(unittest.TestCase):
    
    def test_score_detail_structure(self):
        detail = ScoreDetail(score=85, level="Good", positives=["Yes"], negatives=["No"])
        self.assertEqual(detail.score, 85)
        self.assertEqual(detail.level, "Good")
        self.assertIn("Yes", detail.positives)
        self.assertIn("No", detail.negatives)

    def test_profile_readme_analyzer(self):
        analyzer = ProfileReadmeAnalyzer()
        content = "# About Me\nHi.\n# Tech Stack\nPython."
        # > 500 chars for bonus
        content += "a" * 501
        
        result = analyzer.analyze(content)
        self.assertIsInstance(result, ScoreDetail)
        self.assertTrue(result.score >= 60) # 20 (About) + 20 (Stack) + 20 (Length)
        self.assertIn("Includes 'About Me' / Introduction", result.positives)
        self.assertIn("Missing Contact / Socials section", result.negatives)
        
    def test_repo_docs_multi_language(self):
        analyzer = RepoDocumentationAnalyzer()
        repo = Repository(
            name="test", 
            readme_content="# Instalação\nExecute.\n```\ncodigo\n```",
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com"
        )
        result = analyzer.analyze(repo)
        self.assertIn("Contains sections: Installation", result.positives)
        self.assertIn("Includes code blocks/examples", result.positives)
        self.assertIn("Short README content", result.negatives)

    def test_maturity_recommendations(self):
        analyzer = MaturityAnalyzer()
        repo = Repository(
            name="test", 
            has_ci=False, 
            has_tests=True, 
            updated_at="2025-01-01T00:00:00Z",
            html_url="http://example.com"
        )
        result = analyzer.analyze(repo)
        self.assertIn("Add CI/CD pipelines (e.g., GitHub Actions)", result.negatives)
        self.assertIn("Testing framework detected", result.positives)

if __name__ == "__main__":
    unittest.main()