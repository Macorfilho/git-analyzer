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
    has_ci: bool = False
    has_docker: bool = False
    has_tests: bool = False
    has_license: bool = False
    dependencies: List[str] = []
    maturity_score: int = 0
    maturity_label: str = "Hobby"
    
    # Advanced Metrics (New)
    conventional_commits_ratio: float = 0.0
    commit_frequency: float = 0.0
    average_message_length: float = 0.0
    repo_documentation_score: int = 0
    code_hygiene_score: int = 0

    # Raw Data Fields
    file_tree: List[str] = []
    dependency_files: Dict[str, str] = Field(default_factory=dict)
    readme_content: Optional[str] = None
    commit_history: List[Dict[str, Any]] = []

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
    avg_repo_docs_score: int
    personal_readme_score: int
    repo_quality_score: int
    overall_score: int
    summary: str
    suggestions: List[Suggestion] = []
    details: Dict[str, Any] = Field(default_factory=dict)
    raw_llm_response: Optional[Dict[str, Any]] = None
    avg_code_hygiene_score: int = 0
