from repo_ast import processDirectory
import os

if __name__ == "__main__":
    cloneRepoPath = './cloned_repos'

    for repoFolder in os.listdir(cloneRepoPath):
        repoPath = os.path.join(cloneRepoPath, repoFolder)

        if os.path.isdir(repoPath):
            print(f"Processing repository: {repoFolder}")
            processDirectory(repoPath)
        else:
            print(f"Skipping non-directory item: {repoFolder}")