# Git Analyzer

A full-stack web application designed to analyze GitHub repositories and provide insights and suggestions for improvement.

## 🎯 Goal
The platform analyzes a GitHub repository to generate a "Maturity Score" and specific, actionable suggestions for improving the repository's health and maintainability.

## 🏗 Tech Stack

### Backend (API)
*   **Python 3.9+**
*   **Flask**: Web framework.
*   **Redis**: Message broker for background tasks.
*   **Ollama**: Local LLM runner for AI analysis.
*   **Pydantic**: Data validation and settings management.
*   **PyGithub**: Interaction with the GitHub API.
*   **Architecture**: Modular, Service-Oriented, with background workers.

### Frontend (UI)
*   **React**: UI Library (Vite build tool).
*   **Tailwind CSS**: Utility-first styling.
*   **Architecture**: Component-based, Hooks pattern.

## 📂 Project Structure

```
git-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/            # Flask Routes
│   │   ├── analyzers/      # Business Logic (Scoring engines)
│   │   ├── core/           # Interfaces & Core Config
│   │   ├── models/         # Pydantic DTOs
│   │   └── services/       # Orchestration & External Providers
│   ├── run.py              # API Entry point
│   ├── worker.py           # Worker Entry point
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/     # UI Components
    │   ├── hooks/          # Custom React Hooks
    │   └── services/       # API calls
    └── ...
```

## 🚀 Getting Started

### Prerequisites
*   Python 3.8+
*   Node.js 16+
*   Redis
*   Ollama (running locally)
*   A [GitHub Personal Access Token](https://github.com/settings/tokens) (Classic) with `public_repo` scope.

### 1. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Configure Environment:
1.  Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
2.  Open `.env` and paste your GitHub Token.

Run the API Server:
```bash
python run.py
```
The API will start at `http://localhost:5000`.

### 2. Worker Setup

In a new terminal, navigate to the backend directory and activate the virtual environment:
```bash
cd backend
source venv/bin/activate
```

Run the Worker:
```bash
python worker.py
```
The worker will connect to Redis and wait for analysis jobs.

### 3. Frontend Setup

In a new terminal, navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Run the Development Server:
```bash
npm run dev
```
The UI will be available at `http://localhost:5173`.

### 4. AI Setup (Ollama)

This project uses **Ollama** to provide advanced profile analysis.

1.  [Download and Install Ollama](https://ollama.com/download).
2.  Start the Ollama service.
3.  Pull the required model (default is `llama3`):
    ```bash
    ollama pull llama3
    ```
    *Note: Ensure Ollama is running on port `11434` (default).*

## 🧪 Features

1.  **Repository Analysis**: Kicks off an asynchronous analysis of a GitHub repository.
2.  **Maturity Score**: Calculates a score based on repository characteristics (Docs, CI/CD, Testing).
3.  **AI Career Coach**: Uses Llama 3 (via Ollama) to act as a "Staff Software Engineer" reviewer, providing:
    *   **Gap Analysis**: Identifying missing skills or tools.
    *   **Career Roadmap**: Actionable steps to reach Senior/Staff level.
    *   **Executive Summary**: A professional assessment of the profile.


## 📝 License
This project is open-source and available under the MIT License.