# GitHub Profile Analyzer

A full-stack web application designed to analyze GitHub profiles and provide actionable feedback to improve professional presence.

## 🎯 Goal
The platform analyzes a user's **UserProfile** (Bio, Location, README) and **Repositories** (Descriptions, Consistency, Languages) to generate a "Professional Score" and specific, actionable suggestions for improvement.

## 🏗 Tech Stack

### Backend (API)
*   **Python 3.9+**
*   **Flask**: Web framework.
*   **Pydantic**: Data validation and settings management.
*   **PyGithub**: Interaction with the GitHub API.
*   **Architecture**: Modular, Service-Oriented, SOLID principles.

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
│   ├── run.py              # Entry point
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

Run the Server:
```bash
python run.py
```
The API will start at `http://localhost:5000`.

### 2. Frontend Setup

Navigate to the frontend directory (open a new terminal):
```bash
cd frontend
```

*Note: If you haven't initialized the React project, you will need to install dependencies first.*

Install dependencies:
```bash
npm install
```

Run the Development Server:
```bash
npm run dev
```
The UI will be available at `http://localhost:5173`.

## 🧪 Features

1.  **Profile Analysis**: Checks for Bio, Location, Avatar, and key README sections (About, Tech Stack, Contact).
2.  **Repository Audit**: Scans last 20 repos for descriptions, language definitions, and engagement (stars/forks).
3.  **Smart Suggestions**: Suggests specific project ideas based on the dominant language found in repositories.
4.  **Scoring System**: Calculates an overall "Professional Score" out of 100.

## 📝 License
This project is open-source and available under the MIT License.
