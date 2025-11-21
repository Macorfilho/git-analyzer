export interface Suggestion {
    category: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
}

export interface CareerRoadmapStep {
    step: string;
    description: string;
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
    maturity_score: number;
    maturity_label: "Production-Grade" | "Prototype" | "Hobby";
    conventional_commits_ratio: number;
    commit_frequency: number;
    average_message_length: number;
    repo_documentation_score: number;
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
    profile_score: number;
    readme_score: number;
    repo_quality_score: number;
    repo_docs_score: number;
    overall_score: number;
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