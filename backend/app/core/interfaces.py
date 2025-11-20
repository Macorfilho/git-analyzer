from abc import ABC, abstractmethod
from app.models.dtos import UserProfile

class IGithubProvider(ABC):
    """
    Abstract Interface for GitHub Data Provider.
    Follows Dependency Inversion Principle.
    """
    
    @abstractmethod
    def get_user_profile(self, username: str) -> UserProfile:
        """
        Fetches the user profile and their repositories.
        
        Args:
            username (str): The GitHub username.
            
        Returns:
            UserProfile: A populated UserProfile DTO.
            
        Raises:
            ValueError: If the user is not found.
            ConnectionError: If there is an issue connecting to the GitHub API.
        """
        pass
