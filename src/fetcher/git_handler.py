import pygit2
from typing import List
import logging
import os

class GitHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def clone_repository(self, url: str, path: str) -> pygit2.Repository:
        try:
            if os.path.exists(path):
                try:
                    repo = pygit2.Repository(path)
                    self.logger.info(f"Repository already exists at path: {path}")
                    return repo
                except pygit2.GitError:
                    # Directory exists but is not a git repository
                    self.logger.info(f"Directory exists but is not a git repository: {path}")
            
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
        
