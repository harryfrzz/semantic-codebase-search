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

res_dict = defaultdict(list)
lang_dict = {"py":"PYTHON","ts":"TYPESCRIPT","js":"JS"} 
# Implemented walkthrough of all files with folder exclusions
def walkthrough_files(extensions=None):
    current_working_dir = os.getcwd()
    file_paths = []
    exclude = set(['Include','Lib','Scripts'])
    for root,dirs, files in os.walk(current_working_dir):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            if extensions is None or file.endswith(tuple(extensions)):
                file_paths.append(os.path.join(root, file))
    return file_paths

# Implemented opening and reading of files
def open_files(file_dir):
    file_contents = []
    for dirs in file_dir:
         with open(dirs, "r", errors="ignore") as file:
             file_contents.append(file.read())
    return file_contents

def split_text(input_code):
    for code in input_code:
        code_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, chunk_size=100, chunk_overlap=0)
        python_docs = code_splitter.create_documents([code])
        return python_docs
    

dirs = walkthrough_files(extensions=[".py"])
inp_code = open_files(dirs)
splitted_text = split_text(inp_code)
print(splitted_text)

