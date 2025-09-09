from data_fetch_split import (
    split_text_by_language, 
    walkthrough_files )
# For testing purpose only
import faiss
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
import time
import os
import hashlib
import json

FAISS_INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "faiss_index")

embeddings = OllamaEmbeddings(
    model="all-minilm:33m",
)

def get_codebase_hash():
    file_data = walkthrough_files()  # Returns dict of {extension: {file_path: content}}
    file_info = []
    
    # Iterate through the dictionary structure
    for extension, files in file_data.items():
        for file_path, content in files.items():
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            file_info.append((file_path, content_hash))
    
    file_info.sort()
    combined = json.dumps(file_info)
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def refresh_embeddings():
    hash_file = os.path.join(FAISS_INDEX_DIR, "codebase_hash.txt")
    current_hash = get_codebase_hash()
    
    if not os.path.exists(hash_file):
        return True, current_hash
    
    try:
        with open(hash_file, 'r') as f:
            stored_hash = f.read().strip()
        return stored_hash != current_hash, current_hash
    except:
        return True, current_hash

def save_codebase_hash(codebase_hash):
    hash_file = os.path.join(FAISS_INDEX_DIR, "codebase_hash.txt")
    with open(hash_file, 'w') as f:
        f.write(codebase_hash)

def embed_code_chunks(batch_size=64):
    print("Starting embedding process...")
    start_time = time.time()
    
    # Create faiss_index directory if it doesn't exist
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    
    # Check if embeddings need to be refreshed
    needs_refresh, current_hash = refresh_embeddings()
    
    # Check if existing embeddings are available and still valid
    index_file = os.path.join(FAISS_INDEX_DIR, "index.faiss")
    if os.path.exists(index_file) and not needs_refresh:
        print(f"Loading existing embeddings from {FAISS_INDEX_DIR}")
        try:
            vector_store = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
            print(f"Successfully loaded existing embeddings with {vector_store.index.ntotal} documents")
            return vector_store
        except Exception as e:
            print(f"Failed to load existing embeddings: {e}")
            print("Creating new embeddings...")
    elif needs_refresh:
        print("Codebase has changed, refreshing embeddings...")
    
    # Initialize FAISS index
    dimension = len(embeddings.embed_query("hello world"))
    index = faiss.IndexFlatL2(dimension)
    vector_store = FAISS(
        embedding_function=embeddings,
        docstore=InMemoryDocstore(),
        index=index,
        index_to_docstore_id={},
    )

    # Get and process documents
    file_data = walkthrough_files()
    splitted_text = split_text_by_language(file_data)
    
    documents_list = []
    for doc in splitted_text:
        document = Document(
            page_content=doc.page_content,
            metadata={
                "filename": doc.metadata['filename'],
                "path": doc.metadata['path'],
                "extension": doc.metadata['extension']
            }
        )
        documents_list.append(document)

    if not documents_list:
        print("No documents found to embed")
        return vector_store

    total_docs = len(documents_list)
    print(f"Embedding {total_docs} documents in batches of {batch_size}")

    # Process documents in batches
    for i in range(0, total_docs, batch_size):
        batch_end = min(i + batch_size, total_docs)
        batch_docs = documents_list[i:batch_end]
        batch_num = (i // batch_size) + 1
        total_batches = (total_docs + batch_size - 1) // batch_size
        
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch_docs)} documents)")
        
        try:
            vector_store.add_documents(documents=batch_docs)
        except Exception as e:
            print(f"Error processing batch {batch_num}: {e}")
            continue

    total_time = time.time() - start_time
    print(f"Embedding completed in {total_time:.2f} seconds")
    print(f"Average time per document: {total_time/total_docs:.3f} seconds")
    
    # Save embeddings to persistent storage
    try:
        print(f"Saving embeddings to {FAISS_INDEX_DIR}")
        vector_store.save_local(FAISS_INDEX_DIR)
        save_codebase_hash(current_hash)
        print("Embeddings and codebase hash saved successfully!")
    except Exception as e:
        print(f"Failed to save embeddings: {e}")
    
    return vector_store
