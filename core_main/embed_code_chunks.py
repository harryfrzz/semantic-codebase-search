from data_fetch_split import (
    split_text_by_language, 
    walkthrough_files )
import faiss
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore

from langchain_core.documents import Document

embeddings = OllamaEmbeddings(
    model="all-minilm:33m",
)

def embed_code_chunks():
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
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
        document = Document(page_content=doc.page_content,
        metadata={
            "filename" : doc.metadata['filename'],
            "path" : doc.metadata['path'],
            "extension": doc.metadata['extension']
            }
        )
        documents_list.append(document)

    vector_store.add_documents(documents=documents_list)

    return vector_store
        