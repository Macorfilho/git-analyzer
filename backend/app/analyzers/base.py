from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.models.dtos import UserProfile

class BaseAnalyzer(ABC):
    """
    Abstract Base Class for all Analyzers.
    Enforces a standard interface for analysis logic.
    """

    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Perform analysis on the provided data.

        Args:
            data (Any): The data to analyze (UserProfile, Repository, etc.)

        Returns:
            Dict[str, Any]: The analysis results, including score and details.
        """
        pass
