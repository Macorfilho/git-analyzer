
import sys
import os
# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.llm_provider import OllamaProvider

def test_ollama():
    print("Testing Ollama Connection...")
    provider = OllamaProvider(model="llama3")
    try:
        # Simple context to test
        context = "User: test_user, Bio: test bio, Repos: None"
        print(f"Sending request to {provider.base_url} with model {provider.model}...")
        result = provider.generate_analysis(context)
        print("Success! Result:")
        print(result)
    except Exception as e:
        print("Failed!")
        print(e)

if __name__ == "__main__":
    test_ollama()
