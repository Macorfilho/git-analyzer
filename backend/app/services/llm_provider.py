import requests
import json
from typing import Dict, Any
from app.core.interfaces import ILLMProvider

class OllamaProvider(ILLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    def generate_analysis(self, context_data: str) -> Dict[str, Any]:
        # Using Chat API
        # REMOVED format="json" to prevent the model from "parsing" the resume into JSON.
        # Instead, we ask it to GENERATE the analysis JSON.
        
        system_content = (
            "You are a GitHub Profile Analyzer. "
            "Your job is to score the profile and provide feedback. "
            "You must return the result as a valid JSON string."
        )
        
        user_content = (
            "Analyze this profile data and calculate scores (0-100).\n"
            "Return ONLY a raw JSON object with this exact schema:\n\n"
            "{\n"
            "  \"profile_score\": <int>,\n"
            "  \"readme_score\": <int>,\n"
            "  \"repo_quality_score\": <int>,\n"
            "  \"overall_score\": <int>,\n"
            "  \"summary\": \"<string>\",\n"
            "  \"suggestions\": [\n"
            "    {\"category\": \"<string>\", \"severity\": \"low|medium|high\", \"message\": \"<string>\"}\n"
            "  ]\n"
            "}\n\n"
            f"PROFILE CONTENT:\n{context_data}"
        )

        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                "stream": False,
                # "format": "json"  <-- Removed to test if it helps adherence
            }
            
            print(f"Sending request to Ollama Chat API ({self.model})...")
            response = requests.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            
            result = response.json()
            raw_response = result['message']['content']
            print(f"Raw LLM Response: {raw_response}") # Debug log
            
            # Clean markdown code blocks which are common in text mode
            cleaned_response = raw_response.strip()
            if "```" in cleaned_response:
                # Extract content between first and last ```
                parts = cleaned_response.split("```")
                # Usually the code block is in the second part (index 1)
                # e.g. "Here is the JSON:\n```json\n{...}\n```"
                if len(parts) >= 3:
                    cleaned_response = parts[1]
                    if cleaned_response.startswith("json"):
                        cleaned_response = cleaned_response[4:]
            
            return json.loads(cleaned_response)
            
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
                "raw_llm_response": {"error": "JSONDecodeError", "raw": raw_response}
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
            
        except requests.exceptions.ConnectionError:
            print("Ollama connection failed. Ensure Ollama is running.")
            return {
                "profile_score": 0,
                "readme_score": 0,
                "repo_quality_score": 0,
                "overall_score": 0,
                "summary": "Analysis unavailable: Could not connect to the AI service (Ollama). Please ensure Ollama is running locally.",
                "suggestions": []
            }
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Raw LLM Response: {raw_response}") # Log raw response for debug
            return {
                "profile_score": 0,
                "readme_score": 0,
                "repo_quality_score": 0,
                "overall_score": 0,
                "summary": "Analysis failed: The AI returned an invalid response format.",
                "suggestions": [],
                "raw_llm_response": {"error": "JSONDecodeError", "raw": raw_response}
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
