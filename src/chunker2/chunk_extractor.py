import os
import json
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from .languages import languageExtensions

def detectLanguage(filePath):
        extension = os.path.splitext(filePath)[1][1:].lower()
        return languageExtensions.get(extension, 'unknown')

def processRepos(root_folder="cloned_repos"):
    mapping = {}
    
    for repoName in os.listdir(root_folder):
        repoPath = os.path.join(root_folder, repoName)
        if os.path.isdir(repoPath):
            processRepo(repoPath, mapping)

    with open(os.path.join(repoPath, "file_chunk_mapping.json"), "w") as f:
        json.dump(mapping, f, indent=2)

def processRepo(repoPath, mapping):
    chunkFolder = os.path.join(repoPath, "chunk_data")
    os.makedirs(chunkFolder, exist_ok=True)
    
    for root, _, files in os.walk(repoPath):
        for file in files:
            filePath = os.path.join(root, file)
            if os.path.isfile(filePath):
                processFile(filePath, chunkFolder, mapping)

def processFile(filePath, chunkFolder, mapping):
    try:
        language = detectLanguage(filePath)
        if language == 'unknown':
            print(f"Skipping file with unknown language: {filePath}")
            return
        reader = SimpleDirectoryReader(input_files=[filePath])
        documents = reader.load_data()
        parser = SentenceSplitter.from_defaults(chunk_size=20000, chunk_overlap=500)
        nodes = parser.get_nodes_from_documents(documents)
        
        relativePath = os.path.relpath(filePath, "cloned_repos")
        chunkFileName = relativePath.replace(os.path.sep, "_") + "_chunks.txt"
        chunkFilePath = os.path.join(chunkFolder, chunkFileName)
        
        with open(chunkFilePath, "w", encoding="utf-8") as f:
            for node in nodes:
                f.write(f"Chunk: {node.text}\n\n")
        
        mapping[filePath] = chunkFilePath
    except Exception as e:
        print(f"Error processing file {filePath}: {str(e)}")

if __name__ == "__main__":
    processRepos()