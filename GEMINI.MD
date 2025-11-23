# GitHub Profile Analyzer - Architecture & Insight Engine Documentation

## 🚀 Project Vision

This project is not just a metadata scanner; it is an **AI-Powered Career Strategist**.
It transitions from simple metric counting to **Deep Data Mining** and **Heuristic Analysis** to provide actionable career roadmaps for software engineers.

---

## 🏗 Architecture: The Async Analysis Pipeline

The system implements an asynchronous "Job Queue" architecture to handle the heavy lifting of deep repository scanning without timing out user requests.

### High-Level Flow

1.  **Client (React)** sends `POST /analyze/<username>`.
2.  **API (Flask)** generates a `job_id`, enqueues the task in **Redis/RQ**, and returns immediately (`202 Accepted`).
3.  **Worker (RQ)** picks up the job:
    - **GithubProvider**: Fetches raw data using **Parallel Threading**.
    - **Collectors**: Extract dependencies and file structures from the raw data.
    - **Insight Engine**: deterministic algorithms calculate scores (Maturity, Hygiene, Docs).
    - **LLM Provider (Ollama)**: Synthesizes a "Career Roadmap" based on the structured data.
4.  **Client** polls `GET /status/<job_id>` until the status is `finished`.

### Key Components

| Component          | Responsibility                       | Key Tech                       |
| :----------------- | :----------------------------------- | :----------------------------- |
| **Backend API**    | Job orchestration & Status reporting | Flask, Blueprints              |
| **Task Queue**     | Background processing management     | Redis, RQ (Redis Queue)        |
| **GithubProvider** | High-performance data fetching       | PyGithub, `ThreadPoolExecutor` |
| **InsightEngine**  | Business logic & Scoring rules       | Python (Pydantic Models)       |
| **LLMProvider**    | Strategic synthesis & Gap analysis   | Ollama (Llama 3), Requests     |
| **Frontend**       | Visualization & Polling              | React, Tailwind, Vite          |

---

## 🧠 The Insight Engine (Business Logic)

The core intelligence resides in `backend/app/services/insight_engine.py`. It uses deterministic heuristics to grade repositories _before_ the AI sees them.

### 1. Maturity Analyzer

Determines if a project is a "Hobby", "Prototype", or "Production-Grade".

- **Signals:** Existence of CI/CD (`.github/workflows`), Tests (`pytest`, `jest`), Docker, and License.
- **Penalty:** "Ghost Projects" (inactive > 1 year) receive a heavy score deduction.
- **Bonus:** DevOps Synergy (Tests + CI together).

### 2. Tech Stack Analyzer

Distinguishes between "Core Skills" and "Experimentation".

- **Core Stack:** Technologies appearing in Production-Grade repositories.
- **Experimentation:** Technologies appearing only in Hobby projects.
- **Deep Parsing:** Parses `package.json`, `requirements.txt`, `go.mod`, `pom.xml`, `Cargo.toml`.

### 3. Commit Hygiene Analyzer

Evaluates the professional habits of the developer.

- **Frequency:** Average days between commits (Consistency).
- **Convention:** Ratio of commits following Conventional Commits (`feat:`, `fix:`, `docs:`).
- **Substance:** Message length check (penalizes empty or "fix" messages).

### 4. Repo Documentation Analyzer

Scores the quality of individual READMEs (distinct from the Profile README).

- **Checks:** Presence of "Usage", "Installation", "Contributing" headers (Multi-language support).
- **Content:** Code blocks presence and text length.

---

## 🤖 AI Integration Strategy

We use a **"Narrative Context"** strategy to prevent AI hallucinations.
Instead of sending raw JSON, the `AnalysisService` constructs a detailed report string:

> _"Repo 'FastAPI-Auth': Python. Maturity: Production (Score: 85). Hygiene: Professional. Docs: Weak (Missing Usage). Status: Active."_

The LLM (Llama 3) acts as a **Senior Engineering Manager**, reading this narrative to:

1.  Perform a **Gap Analysis** (e.g., "Strong Backend, but missing Cloud evidence").
2.  Generate a **Career Roadmap** (3-5 strategic steps).

---

## 🛠 Setup & Requirements

### Dependencies

- **Python 3.9+**
- **Node.js 16+**
- **Redis Server** (Must be running for the worker)
- **Ollama** (Running locally with `llama3`)

### Environment Variables (`.env`)

```env
GITHUB_TOKEN=ghp_your_token...
REDIS_URL=redis://localhost:6379
PORT=5000
```
