from data_fetch_split import (
    split_text_by_language, 
    walkthrough_files )
# import faiss
# from langchain_community.vectorstores import FAISS

file_data = walkthrough_files(extensions=[".py", ".js", ".ts",".txt"])
splitted_text = split_text_by_language(file_data)
for doc in splitted_text:
    print(f"File: {doc.metadata['filename']}.{doc.metadata['extension']}")
    print(f"{doc.page_content}")

# embeddings = OllamaEmbeddings(
#     model="qllama/bge-small-en-v1.5",
# )


# Implement embedding functionality using bge model
def embed_code_chunks():
    return None