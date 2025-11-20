from typing import List
from app.models.dtos import Repository, Suggestion

class SuggestionEngine:
    """
    Generates project suggestions based on the user's existing repositories.
    """

    def generate_suggestions(self, repositories: List[Repository]) -> List[Suggestion]:
        """
        Analyzes the primary languages used in repositories and suggests new projects.
        """
        languages = {}
        for repo in repositories:
            if repo.language:
                lang = repo.language.lower()
                languages[lang] = languages.get(lang, 0) + 1
        
        # Determine dominant language
        if not languages:
            return [Suggestion(category="General", severity="medium", message="Add some code to your repositories to get specific suggestions!")]

        dominant_lang = max(languages, key=languages.get)
        
        suggestions = []

        # Simple logic map
        if dominant_lang == "python":
            suggestions.append(Suggestion(category="Project Idea", severity="low", message="Build a CLI tool using 'Click' or 'Typer'."))
            suggestions.append(Suggestion(category="Project Idea", severity="medium", message="Create a REST API with FastAPI and SQLModel."))
            suggestions.append(Suggestion(category="Project Idea", severity="high", message="Develop a data analysis dashboard using Streamlit."))
        elif dominant_lang in ["javascript", "typescript"]:
             suggestions.append(Suggestion(category="Project Idea", severity="low", message="Build a To-Do app with LocalStorage."))
             suggestions.append(Suggestion(category="Project Idea", severity="medium", message="Create a weather dashboard using a public API."))
             suggestions.append(Suggestion(category="Project Idea", severity="high", message="Develop a full-stack MERN application."))
        elif dominant_lang == "java":
             suggestions.append(Suggestion(category="Project Idea", severity="medium", message="Build a Spring Boot REST API."))
        elif dominant_lang == "go":
             suggestions.append(Suggestion(category="Project Idea", severity="medium", message="Create a high-performance web scraper."))
        elif dominant_lang == "rust":
             suggestions.append(Suggestion(category="Project Idea", severity="high", message="Write a simple operating system kernel or a game engine."))
        else:
             suggestions.append(Suggestion(category="Project Idea", severity="medium", message=f"Build a portfolio website highlighting your {dominant_lang} projects."))
             suggestions.append(Suggestion(category="Project Idea", severity="low", message="Contribute to an open-source project."))
             suggestions.append(Suggestion(category="Project Idea", severity="high", message="Create a detailed technical blog."))

        # Ensure we return exactly 3 or fill up
        while len(suggestions) < 3:
             suggestions.append(Suggestion(category="General", severity="low", message="Document your learning journey in a README."))

        return suggestions[:3]
