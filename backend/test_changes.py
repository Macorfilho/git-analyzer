import unittest
import json
from datetime import datetime, timedelta
from app.services.collectors import DependencyCollector
from app.services.insight_engine import CommitHygieneAnalyzer

class TestNewFeatures(unittest.TestCase):
    def test_dependency_collector_extended(self):
        collector = DependencyCollector()
        
        dependency_files = {
            "build.gradle": """
                plugins {
                    id 'java'
                }
                dependencies {
                    implementation 'com.google.guava:guava:30.1-jre'
                    implementation("org.springframework.boot:spring-boot-starter-web")
                    testImplementation 'junit:junit:4.13.2'
                }
            """,
            "go.mod": """
                module example.com/my/thing

                go 1.16

                require (
                    github.com/gin-gonic/gin v1.7.4
                    github.com/go-redis/redis/v8 v8.11.3
                )
                
                require google.golang.org/grpc v1.40.0
            """,
            "Cargo.toml": """
                [package]
                name = "my-crate"
                version = "0.1.0"

                [dependencies]
                serde = "1.0"
                tokio = { version = "1", features = ["full"] }
                
                [dev-dependencies]
                criterion = "0.3"
            """,
            "pom.xml": """
                <project>
                    <dependencies>
                        <dependency>
                            <groupId>org.apache.commons</groupId>
                            <artifactId>commons-lang3</artifactId>
                            <version>3.12.0</version>
                        </dependency>
                    </dependencies>
                </project>
            """
        }
        
        deps = collector.analyze(dependency_files)
        
        # Gradle
        self.assertTrue(any("guava" in d for d in deps), f"Deps: {deps}")
        self.assertTrue(any("spring-boot-starter-web" in d for d in deps), f"Deps: {deps}")
        
        # Go
        self.assertTrue(any("gin-gonic/gin" in d for d in deps), f"Deps: {deps}")
        self.assertTrue(any("grpc" in d for d in deps), f"Deps: {deps}")
        
        # Rust
        self.assertIn("serde", deps)
        self.assertIn("tokio", deps)
        
        # Maven
        self.assertIn("commons-lang3", deps)

    def test_commit_hygiene_scoring(self):
        analyzer = CommitHygieneAnalyzer()
        
        # Case 1: Perfect Score
        # Freq < 7 days (40pts), Msg > 15 (30pts), Conv 100% (30pts) -> 100
        now = datetime.now()
        history_perfect = [
            {"date": (now - timedelta(days=1)).isoformat(), "message": "feat: add new feature with long description"},
            {"date": (now - timedelta(days=3)).isoformat(), "message": "fix: resolve critical bug in system"},
            {"date": (now - timedelta(days=5)).isoformat(), "message": "docs: update readme with instructions"}
        ]
        label, cc, avg_days = analyzer.analyze(history_perfect)
        self.assertEqual(label, "Professional")
        self.assertEqual(cc, 1.0)
        
        # Case 2: Low Score
        # Freq > 30 days (0pts), Msg short (0pts), Conv 0% (0pts) -> 0
        history_bad = [
            {"date": (now - timedelta(days=40)).isoformat(), "message": "fix"},
            {"date": (now - timedelta(days=80)).isoformat(), "message": "wip"}
        ]
        label, cc, avg_days = analyzer.analyze(history_bad)
        self.assertTrue(label in ["Inactive", "Standard"], f"Label was {label}")
        self.assertEqual(cc, 0.0)
        
        # Case 3: Active but messy
        # Freq < 7 days (40pts), Msg short (0pts), Conv 0% (0pts) -> 40 -> "Active" or "Standard"
        history_messy = [
             {"date": (now - timedelta(days=1)).isoformat(), "message": "stuff"},
             {"date": (now - timedelta(days=2)).isoformat(), "message": "more stuff"}
        ]
        label, cc, avg_days = analyzer.analyze(history_messy)
        self.assertEqual(label, "Active") # Score 40 -> Active
        
if __name__ == "__main__":
    unittest.main()
