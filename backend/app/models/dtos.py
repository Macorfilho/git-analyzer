from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ScoreDetail(BaseModel):
    score: int
    level: str
    positives: List[str] = []
    negatives: List[str] = []

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
    
    # Scores as Detailed Objects
    maturity_score: ScoreDetail = Field(default_factory=lambda: ScoreDetail(score=0, level="Hobby"))
    repo_documentation_score: ScoreDetail = Field(default_factory=lambda: ScoreDetail(score=0, level="None"))
    code_hygiene_score: ScoreDetail = Field(default_factory=lambda: ScoreDetail(score=0, level="Standard"))
    
    # Deprecated/Derived Simple Fields
    maturity_label: str = "Hobby"
    
    # Metrics
    conventional_commits_ratio: float = 0.0
    commit_frequency: float = 0.0
    average_message_length: float = 0.0
    
    # Recommendations
    recommendations: List[str] = []

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
    
    # Detailed Scores
    profile_score: ScoreDetail
    personal_readme_score: ScoreDetail
    avg_repo_docs_score: ScoreDetail
    avg_code_hygiene_score: ScoreDetail
    repo_quality_score: ScoreDetail
    overall_score: ScoreDetail
    
    summary: str
    suggestions: List[Suggestion] = []
    details: Dict[str, Any] = Field(default_factory=dict)
    raw_llm_response: Optional[Dict[str, Any]] = None
