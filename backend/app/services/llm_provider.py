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
            "You are a Senior Technical Recruiter and Engineering Manager. "
            "You evaluate GitHub profiles to assess technical proficiency, documentation skills, and personal branding. "
            "You provide constructive, actionable feedback in strict JSON format."
        )
        
        user_content = (
            f"PROFILE DATA START:\n{context_data}\nPROFILE DATA END\n\n"
            "---------------------------------------------------\n"
            "INSTRUCTIONS:\n"
            "1. Analyze the provided GitHub Bio, Repository List, and Profile README.\n"
            "2. Look for patterns in their tech stack, quality of documentation, and consistency of activity.\n"
            "3. Calculate scores (0-100) reflecting their readiness for a professional engineering role.\n"
            "4. Return a SINGLE JSON object. No text before or after.\n\n"
            "REQUIRED OUTPUT SCHEMA:\n"
            "{\n"
            "  \"profile_score\": <int>,\n"
            "  \"readme_score\": <int>,\n"
            "  \"repo_quality_score\": <int>,\n"
            "  \"overall_score\": <int>,\n"
            "  \"summary\": \"<string: Detailed executive summary highlighting specific strengths and critical gaps in the portfolio>\",\n"
            "  \"career_roadmap\": [\n"
            "    {\"step\": \"<string>\", \"description\": \"<string>\"}\n"
            "  ],\n"
            "  \"suggestions\": [\n"
            "    {\"category\": \"<string>\", \"severity\": \"low|medium|high\", \"message\": \"<string: Specific, actionable advice. Do not give generic advice like 'add more repos'. Suggest specific technologies or project types based on their current stack.>\"}\n"
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