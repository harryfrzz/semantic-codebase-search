from embed_code_chunks import embed_code_chunks
import os
import sys
import requests

FAISS_INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "faiss_index")

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def generate(self, model, prompt, stream=False):
        url = f"{self.base_url}/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {e}")
            return None

ollama_client = OllamaClient()

def search_codebase(user_query):
    vector_store = embed_code_chunks(batch_size=64)
    results = vector_store.similarity_search(user_query, k=10)
        
    context = ""
    for doc in results:
        context += f"**File:** {doc.metadata.get('filename', 'Unknown')}\n"
        context += f"**Path:** `{doc.metadata.get('path', 'Unknown')}`\n"
        context += f"**Extension:** {doc.metadata.get('extension', 'Unknown')}\n"
        context += f"**Code:** {doc.page_content}\n"
    return context

def get_response(user_query, context):
    prompt = f"""
            You are a code assistant. Based on the user's query: "{user_query}"

            Analyze the following code snippets and provide a response in MARKDOWN format with:

            1. **File Paths**: List all relevant file paths
            2. **Code Explanation**: Explain what the provided code does and how it works (only use the code that are provided as snippets)

            Use proper markdown formatting with headers, code blocks, and lists.
            Avoid using special Unicode characters like em-dashes, en-dashes, or fancy quotes.

            Here are the relevant code snippets:
            {context}

            Respond in markdown format only using standard ASCII characters.
            """
    
    try:
        result = ollama_client.generate("gpt-oss:20b", prompt)
        if result and "response" in result:
            return result["response"]
        else:
            return "Error: Could not get response from Ollama"
    except Exception as e:
        return f"Error: Failed to get response from Ollama. {str(e)}"

def check_ollama_connection():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            if "gpt-oss:20b" in model_names:
                print("Ollama is running and gpt-oss:20b model is available")
                return True
            else:
                print(f"gpt-oss:20b model not found")
                return False
        else:
            print("Ollama is not responding")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama. Make sure it's running on localhost:11434")
        return False

def main():
    if not check_ollama_connection():
        sys.exit(1)
    
    if len(sys.argv) < 2:
        sys.exit(1)
        
    user_query = " ".join(sys.argv[1:])
        
    print(f"# Searching codebase for: '{user_query}'...")
    context = search_codebase(user_query)
        
    if not context.strip() or context.startswith("## Error"):
        print(f"# Search Error\nNo relevant code found or error occurred:\n{context}")
        return
    
    print("# Generating response using Ollama...")        
    response = get_response(user_query, context)
        
    print(f"# Search Results for: '{user_query}'\n")
    print(response)
        

if __name__ == "__main__":
    main()