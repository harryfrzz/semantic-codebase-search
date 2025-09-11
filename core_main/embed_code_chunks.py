from data_fetch_split import (
    split_text_by_language, 
    walkthrough_files )
import faiss
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
import os

FAISS_INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "faiss_index")

embeddings = OllamaEmbeddings(
    model="all-minilm:33m",
)

def embed_code_chunks(batch_size=32):
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    
    index_file = os.path.join(FAISS_INDEX_DIR, "index.faiss")
    if os.path.exists(index_file):
        print(f"⚡ Loading existing embeddings from {FAISS_INDEX_DIR}")
        try:
            vector_store = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
            print(f"Successfully loaded existing embeddings with {vector_store.index.ntotal} documents")
            return vector_store
        except Exception as e:
            print(f"Failed to load existing embeddings: {e}")
            print("Creating new embeddings...")
    
    dimension = len(embeddings.embed_query("test"))
    index = faiss.IndexFlatL2(dimension)
    vector_store = FAISS(
        embedding_function=embeddings,
        docstore=InMemoryDocstore(),
        index=index,
        index_to_docstore_id={},
    )

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
        return vector_store

    total_docs = len(documents_list)
    print(f"Embedding {total_docs} documents in batches of {batch_size}")

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
    
    try:
        print(f"Saving embeddings to {FAISS_INDEX_DIR}")
        vector_store.save_local(FAISS_INDEX_DIR)
        print("Embeddings saved successfully!")
    except Exception as e:
        print(f"Failed to save embeddings: {e}")
    
    return vector_store
