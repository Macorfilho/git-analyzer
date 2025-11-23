import unittest
from app.services.insight_engine import ProfileReadmeAnalyzer

class TestProfileReadmeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ProfileReadmeAnalyzer()
        
    def test_empty_content(self):
        self.assertEqual(self.analyzer.analyze(None), 0)
        self.assertEqual(self.analyzer.analyze(""), 0)
        
    def test_basic_sections(self):
        content = """
        # About Me
        I am a developer.
        
        ## Skills
        Python, JS.
        
        ## Contact
        Email me.
        """
        # Expect 20 (About) + 20 (Skills) + 20 (Contact) = 60
        self.assertEqual(self.analyzer.analyze(content), 60)
        
    def test_stats_and_length(self):
        # Create a long string > 500 chars
        filler = "a" * 501
        content = f"""
        Hi, I'm a dev.
        ![Stats](https://github-readme-stats.vercel.app/api?username=test)
        {filler}
        """
        # Expect 20 (About/Intro "Hi, I'm") + 20 (Stats) + 20 (Length) = 60
        self.assertEqual(self.analyzer.analyze(content), 60)

    def test_full_score(self):
        content = """
        # Introduction
        Hi, I'm a full stack engineer.
        
        ## Tech Stack
        - Python
        - React
        
        ## Socials
        - Twitter
        - LinkedIn
        
        ![GitHub Trophy](https://github-profile-trophy.vercel.app/?username=test)
        
        """ + ("Lorem ipsum " * 50) # Ensure > 500 chars
        
        # 20 (Intro) + 20 (Stack) + 20 (Socials) + 20 (Stats) + 20 (Length) = 100
        self.assertEqual(self.analyzer.analyze(content), 100)

if __name__ == "__main__":
    unittest.main()
