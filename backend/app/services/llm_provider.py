import requests
import json
from typing import Dict, Any
from app.core.interfaces import ILLMProvider

class OllamaProvider(ILLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    def generate_analysis(self, context_data: str) -> Dict[str, Any]:
        # Define the strict schema in the system prompt to guide the model
        system_content = (
            "You are a strict Code Quality Auditor and Data Analyst. "
            "Your ONLY purpose is to evaluate GitHub metrics and repository quality. "
            "You DO NOT care about the user's job history, education, or resume details. "
            "You speak only in JSON."
        )
        
        user_content = (
            f"PROFILE DATA START:\n{context_data}\nPROFILE DATA END\n\n"
            "---------------------------------------------------\n"
            "INSTRUCTIONS:\n"
            "1. Ignore all resume/CV text in the profile data (e.g., 'Education', 'Experience').\n"
            "2. Focus on: Repository descriptions, languages used, star counts, and documentation quality.\n"
            "3. Calculate the following scores (0-100) based ONLY on the evidence above.\n"
            "4. Return a SINGLE JSON object. No text before or after.\n\n"
            "REQUIRED OUTPUT SCHEMA:\n"
            "{\n"
            "  \"profile_score\": <int>,\n"
            "  \"readme_score\": <int>,\n"
            "  \"repo_quality_score\": <int>,\n"
            "  \"overall_score\": <int>,\n"
            "  \"summary\": \"<string: 1-2 sentences max>\",\n"
            "  \"suggestions\": [\n"
            "    {\"category\": \"<string>\", \"severity\": \"low|medium|high\", \"message\": \"<string>\"}\n"
            "  ]\n"
            "}"
        )

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                "stream": False,
                "format": "json"
            }
            
            print(f"Sending request to Ollama Chat API ({self.model})...")
            response = requests.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            
            result = response.json()
            raw_response = result['message']['content']
            print(f"Raw LLM Response: {raw_response}")
            
            return json.loads(raw_response)
            
        except requests.exceptions.ConnectionError:
            print("Ollama connection failed. Ensure Ollama is running.")
            return {
                "profile_score": 0,
                "readme_score": 0,
                "repo_quality_score": 0,
                "overall_score": 0,
                "summary": "Analysis unavailable: Could not connect to the AI service (Ollama).",
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