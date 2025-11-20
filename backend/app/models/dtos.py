from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Repository(BaseModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    updated_at: str
    html_url: str

class UserProfile(BaseModel):
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    public_repos: int
    followers: int
    following: int
    avatar_url: str
    html_url: str
    readme_content: Optional[str] = None
    repositories: List[Repository] = []

class Suggestion(BaseModel):
    category: str
    severity: str  # e.g., "low", "medium", "high"
    message: str

class AnalysisReport(BaseModel):
    username: str
    profile_score: int
    readme_score: int
    repo_quality_score: int
    overall_score: int
    summary: str
    suggestions: List[Suggestion] = []
    details: Dict[str, Any] = Field(default_factory=dict)
    raw_llm_response: Optional[Dict[str, Any]] = None
