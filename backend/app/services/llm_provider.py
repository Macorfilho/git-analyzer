import requests
import json
import time
from requests.adapters import HTTPAdapter
from typing import Dict, Any
from app.core.interfaces import ILLMProvider

class OllamaProvider(ILLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    def generate_analysis(self, context_data: str) -> Dict[str, Any]:
        # Define the strict schema in the system prompt to guide the model
        system_content = (
            "You are a Senior Technical Recruiter and Engineering Staff Manager at a top-tier tech company. "
            "You evaluate software engineering portfolios to assess candidate readiness for senior roles. "
            "Your tone is direct, critical, professional, and inspiring. You do not sugarcoat weaknesses, "
            "but you provide clear strategic direction for growth. You focus deeply on architectural maturity, "
            "engineering standards, and the 'why' behind technical choices."
        )
        
        user_content = (
            f"PROFILE DATA START:\n{context_data}\nPROFILE DATA END\n\n"
            "---------------------------------------------------\n"
            "INSTRUCTIONS:\n"
            "1. Analyze the 'Calculated Metrics' and 'Repo Summaries' deeply.\n"
            "2. Perform a Gap Analysis: What is missing for them to be a Senior/Staff Engineer? (e.g., lack of CI/CD, outdated stack, no testing).\n"
            "3. Create a 'Career Roadmap': 3-5 actionable steps (e.g., 'Master Kubernetes', 'Implement Unit Tests').\n"
            "   - ROADMAP GUARANTEE: If the user portfolio is empty or lacks sufficient data for a custom plan, generate a 'Foundational Career Roadmap' with standard industry steps (e.g., Learn Gitflow, Build a Fullstack App).\n"
            "4. RETURN THE 'Average Repo Documentation Score' PROVIDED IN THE INPUT AS 'readme_score' IN THE JSON.\n"
            "5. Return a SINGLE JSON object.\n\n"
            "CONSTRAINT: Do NOT provide generic advice. Reference specific data points from the provided context (e.g., 'Your repository X lacks CI/CD').\n\n"
            "SUMMARY GENERATION INSTRUCTIONS:\n"
            "Write a comprehensive, three-paragraph executive summary. Do NOT be brief. Elaborate on your findings.\n"
            "- Paragraph 1: Professional Persona & Strengths. Analyze what they do well based on the evidence.\n"
            "- Paragraph 2: Critical Weaknesses/Gaps. Identify major gaps, red flags (like 'Ghost Projects' or poor hygiene), and missed opportunities.\n"
            "- Paragraph 3: Strategic Potential. Assess readiness for Senior roles and provide a high-level verdict.\n\n"
            "REQUIRED OUTPUT SCHEMA:\n"
            "{\n"
            "  \"profile_score\": <int: 0-100 based on overall impression>,\n"
            "  \"readme_score\": <int: value from input 'Average Repo Documentation Score'>,\n"
            "  \"repo_quality_score\": <int: 0-100 based on Maturity/Hygiene signals>,\n"
            "  \"overall_score\": <int: weighted average>,\n"
            "  \"summary\": \"<string: Three-paragraph executive summary>\",\n"
            "  \"career_roadmap\": [\n"
            "    {\"step\": \"<string: Title>\", \"description\": \"<string: Detail>\"}\n"
            "  ],\n"
            "  \"suggestions\": [\n"
            "    {\"category\": \"<string>\", \"severity\": \"low|medium|high\", \"message\": \"<string>\"}\n"
            "  ]\n"
            "}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            "stream": False,
            "format": "json"
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Sending request to Ollama Chat API ({self.model})... (Attempt {attempt + 1}/{max_retries})")
                # Increased timeout to 120 seconds for large contexts/cold starts
                response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
                response.raise_for_status()
                
                result = response.json()
                raw_response = result['message']['content']
                print(f"Raw LLM Response: {raw_response}")
                
                return json.loads(raw_response)
                
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    print("Retrying in 5s...")
                    time.sleep(5)
                else:
                    print("Ollama connection failed after multiple attempts. Ensure Ollama is running and model is pulled.")
                    return {
                        "profile_score": 0,
                        "readme_score": 0,
                        "repo_quality_score": 0,
                        "overall_score": 0,
                        "summary": "Analysis unavailable: Could not connect to the AI service (Ollama) or timeout occurred.",
                        "suggestions": []
                    }
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                return {
                    "profile_score": 0,
                    "readme_score": 0,
                    "repo_quality_score": 0,
                    "overall_score": 0,
                    "summary": "Analysis failed: Invalid JSON response from AI.",
                    "suggestions": [],
                    "raw_llm_response": {"error": "JSONDecodeError"}
                }
            except Exception as e:
                print(f"LLM Provider Error: {e}")
                return {
                    "profile_score": 0,
                    "readme_score": 0,
                    "repo_quality_score": 0,
                    "overall_score": 0,
                    "summary": f"Analysis failed due to an error: {str(e)}",
                    "suggestions": []
                }
        
        return {
            "profile_score": 0,
            "readme_score": 0,
            "repo_quality_score": 0,
            "overall_score": 0,
            "summary": "Analysis unavailable: Unknown error.",
            "suggestions": []
        }
