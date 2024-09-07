from repo_ast import processDirectory
import os

if __name__ == "__main__":
    clone_repo_path = './src/ast_generator/example_repos'

    for repo_folder in os.listdir(clone_repo_path):
        repo_path = os.path.join(clone_repo_path, repo_folder)
        
        if os.path.isdir(repo_path):
            print(f"Processing repository: {repo_folder}")
            processDirectory(repo_path)
        else:
            print(f"Skipping non-directory item: {repo_folder}")