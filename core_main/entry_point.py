import os
import sys
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from embed_code_chunks import embed_code_chunks

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# TODO - Improve responses
# TODO - Integrate local LLM reasoning

client = InferenceClient(
    provider="auto",
    api_key=os.environ["HF_TOKEN"],
)

def search_codebase(user_query):
    vector_store = embed_code_chunks()
    results = vector_store.similarity_search(user_query, k=5)
        
    context = ""
    for i, doc in enumerate(results, 1):
        context += f"\n### Result {i}\n"
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

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
        
    return completion.choices[0].message.content

def main():
    if len(sys.argv) < 2:
        print("# Usage Error\nUsage: python entry_point.py <query>")
        sys.exit(1)
        
    user_query = " ".join(sys.argv[1:])
        
    context = search_codebase(user_query)
        
    if not context.strip() or context.startswith("## Error"):
        print(f"# Search Error\nNo relevant code found or error occurred:\n{context}")
        return
            
    response = get_response(user_query, context)
        
    print(f"# Search Results for: '{user_query}'\n")
    print(response)
        

if __name__ == "__main__":
    main()