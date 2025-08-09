import os

# embeddings = OllamaEmbeddings(
#     model="qllama/bge-small-en-v1.5",
# )


#Implemented walkthrough of all files with folder exclusions
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
#
def open_files(file_dir):
    file_contents = []
    for dirs in file_dir:
         with open(dirs, "r", errors="ignore") as file:
             file_contents.append(file.read())
    return file_contents

dirs = walkthrough_files(extensions=[".py"])
print(open_files(dirs))
