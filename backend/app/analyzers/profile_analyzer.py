from typing import Dict, Any, List
from app.analyzers.base import BaseAnalyzer
from app.models.dtos import UserProfile

class ProfileAnalyzer(BaseAnalyzer):
    """
    Analyzes the user's profile README and general profile completeness.
    """

    def analyze(self, user_profile: UserProfile) -> Dict[str, Any]:
        """
        Analyzes the UserProfile DTO.

        Checks for:
        - Bio presence
        - Location
        - README content (Key sections: "About Me", "Tech Stack", "Contact")
        """
        score = 0
        max_score = 100
        missing_elements = []
        details = {}

        # 1. Basic Profile Checks (30 points)
        if user_profile.bio:
            score += 10
        else:
            missing_elements.append("Bio")

        if user_profile.location:
            score += 5
        else:
            missing_elements.append("Location")
        
        if user_profile.avatar_url:
             score += 5
        
        if user_profile.name:
            score += 10
        else:
            missing_elements.append("Name")

        # 2. README Analysis (70 points)
        readme = user_profile.readme_content
        if readme:
            readme_lower = readme.lower()
            
            sections_to_check = {
                "About Me": ["about me", "introduction", "who am i"],
                "Tech Stack": ["tech stack", "technologies", "skills", "built with", "languages"],
                "Contact": ["contact", "reach me", "socials", "links"]
            }

            section_score = 70 / len(sections_to_check)
            
            for section, keywords in sections_to_check.items():
                found = any(keyword in readme_lower for keyword in keywords)
                if found:
                    score += section_score
                else:
                    missing_elements.append(f"README Section: {section}")
            
            details['readme_length'] = len(readme)
        else:
            missing_elements.append("Profile README")

        return {
            "score": round(score),
            "missing_elements": missing_elements,
            "details": details
        }
