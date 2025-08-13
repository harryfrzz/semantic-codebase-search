# This file is for going through all the files in a directory, 
# open and read it contents and converting that data to vectors and then using faiss to store the vectors and for semantic search
import os
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from collections import defaultdict

# embeddings = OllamaEmbeddings(
#     model="qllama/bge-small-en-v1.5",
# )

# TODO - Pass extension, file/folder exclusions as arguments
# TODO - Use defaultdict for lang_dict

res_dict = defaultdict(dict)  # Changed from defaultdict(list) to defaultdict(dict)
lang_dict = {
    "py": Language.PYTHON, 
    "ts": Language.TS, 
    "js": Language.JS,
    "cpp": Language.CPP,
    "cc": Language.CPP,
    "cxx": Language.CPP,
    "c": Language.C,
    "go": Language.GO,
    "java": Language.JAVA,
    "kt": Language.KOTLIN,
    "php": Language.PHP,
    "proto": Language.PROTO,
    "rst": Language.RST,
    "rb": Language.RUBY,
    "rs": Language.RUST,
    "scala": Language.SCALA,
    "swift": Language.SWIFT,
    "md": Language.MARKDOWN,
    "tex": Language.LATEX,
    "html": Language.HTML,
    "htm": Language.HTML,
    "sol": Language.SOL,
    "cs": Language.CSHARP,
    "cob": Language.COBOL,
    "lua": Language.LUA,
    "pl": Language.PERL,
    "hs": Language.HASKELL,
    "ex": Language.ELIXIR,
    "exs": Language.ELIXIR,
    "ps1": Language.POWERSHELL,
    "vb": Language.VISUALBASIC6
}

# Implemented walkthrough of all files with folder exclusions
def walkthrough_files(extensions=None):
    current_working_dir = os.getcwd()
    exclude = set(['Include','Lib','Scripts'])
    
    for root, dirs, files in os.walk(current_working_dir):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            if extensions is None or file.endswith(tuple(extensions)):
                file_path = os.path.join(root, file)
                filename, file_ext = os.path.splitext(file)
                file_ext = file_ext.lstrip('.')
                
                try:
                    with open(file_path, "r", errors="ignore") as f:
                        file_content = f.read()
                    
                    res_dict[file_ext][filename] = file_content
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    return res_dict

def split_text_by_language(file_extension_dict):
    all_documents = []
    for extension, files in file_extension_dict.items():
        language = lang_dict.get(extension)
        
        if language:
            code_splitter = RecursiveCharacterTextSplitter.from_language(
                language=language, 
                chunk_size=300, 
                chunk_overlap=0
            )
        else:
            code_splitter = RecursiveCharacterTextSplitter(
                chunk_size=300, 
                chunk_overlap=0
            )
        
        for filename, code in files.items():
            docs = code_splitter.create_documents([code])
            for doc in docs:
                doc.metadata = {
                    "filename": filename,
                    "extension": extension,
                    "language": language.value if language else "text"
                }
            all_documents.extend(docs)
    
    return all_documents

file_data = walkthrough_files(extensions=[".py", ".js", ".ts",".txt"])
splitted_text = split_text_by_language(file_data)
print(f"Total documents created: {len(splitted_text)}")
for doc in splitted_text:
    print(f"File: {doc.metadata['filename']}.{doc.metadata['extension']}")
    print(f"{doc.page_content}")