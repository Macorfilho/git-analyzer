export interface Suggestion {
    category: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
}

export interface CareerRoadmapStep {
    step: string;
    description: string;
}

export interface ScoreDetail {
    value: number;
    label: string;
    pros: string[];
    cons: string[];
}

export interface Repository {
    name: string;
    description?: string;
    language?: string;
    stargazers_count: number;
    forks_count: number;
    updated_at: string;
    html_url: string;
    has_ci: boolean;
    has_docker: boolean;
    has_tests: boolean;
    has_license: boolean;
    dependencies: string[];
    maturity_score: ScoreDetail;
    maturity_label: "Production-Grade" | "Prototype" | "Hobby";
    conventional_commits_ratio: number;
    commit_frequency: number;
    average_message_length: number;
    repo_documentation_score: ScoreDetail;
    code_hygiene_score: ScoreDetail;
    recommendations: string[];
    is_ghost?: boolean;
}

export interface AnalysisDetails {
    repo_count?: number;
    followers?: number;
    public_repos?: number;
    core_stack?: string[];
    experimentation_stack?: string[];
    career_roadmap?: CareerRoadmapStep[];
    repositories?: Repository[];
    [key: string]: unknown;
}

export interface AnalysisReport {
    username: string;
    profile_score: ScoreDetail;
    avg_repo_docs_score: ScoreDetail;
    personal_readme_score: ScoreDetail;
    repo_quality_score: ScoreDetail;
    overall_score: ScoreDetail;
    avg_code_hygiene_score: ScoreDetail;
    summary: string;
    suggestions: Suggestion[];
    details: AnalysisDetails;
    raw_llm_response?: Record<string, any>;
}

export interface ApiError {
    error: string;
    details?: string;
}

export interface JobStatus {
    job_id: string;
    status: 'queued' | 'started' | 'deferred' | 'finished' | 'failed' | 'unknown';
    result?: AnalysisReport;
    error?: string;
}