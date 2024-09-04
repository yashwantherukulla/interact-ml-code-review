import pygit2
from typing import List
import logging

class GitHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def clone_repository(self, url: str, path: str) -> pygit2.Repository:
        try:
            if pygit2.Repository(path):
                self.logger.info(f"Repository already exists at path: {path}")
                return pygit2.Repository(path)
            
            repo = pygit2.clone_repository(url, path)
            return repo
        except pygit2.GitError as e:
            self.logger.error(f"Error while cloning repository: {e}")
            raise e
        
    def get_latest_commit(self, repo: pygit2.Repository) -> pygit2.Commit:
        try:
            return repo.head.peel(pygit2.Commit)
        except pygit2.GitError as e:
            self.logger.error(f"Error while getting latest commit: {e}")
            raise e
        
    def get_file_content(self, repo: pygit2.Repository, file_path: str) -> str:
        try:
            file = repo[file_path]
            return file.data.decode("utf-8")
        except pygit2.GitError as e:
            self.logger.error(f"Error while getting file content: {e}")
            raise e
        
# if __name__ == "__main__":
#     git_handler = GitHandler()
#     url = "https://github.com/yashwantherukulla/regit"
#     path = "./cloned_repos/regit"
#     repo = git_handler.clone_repository(url, path)
