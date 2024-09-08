import os
from typing import List, Dict
import logging
from .git_handler import GitHandler
import pygit2
import shutil

class RepositoryManager:
    def __init__(self, git_handler: GitHandler):
        self.logger = logging.getLogger(__name__)
        self.git_handler = git_handler
        self.repos: Dict[str, str] = {} #url, path
        self.logger = logging.getLogger(__name__) #why is there self.logger twice here?

    def clone_repository(self, url: str, base_path: str) -> str:
        repo_name = url.split("/")[-1].replace(".git", "")
        path = os.path.join(base_path, repo_name)
        if url in self.repos:
            self.logger.info(f"Repository already exists at path: {self.repos[url]}")
            return self.repos[url]
    
        try:
            self.git_handler.clone_repository(url, path)
            self.repos[url] = path
            self.logger.info(f"Repository cloned at path: {path}")
            return path
    
        except pygit2.GitError as e:
            self.logger.error(f"GitError while cloning repository: {e}")
            raise
        except OSError as e:
            self.logger.error(f"OSError while cloning repository: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while cloning repository: {e}")
            raise
        
    def update_repository(self, url: str) -> str:
        if url not in self.repos:
            raise ValueError(f"Repository not found at path: {self.repos[url]}")
        
        local_path = self.repos[url]
        repo = pygit2.Repository(local_path)
        
        try:
            repo.remotes["origin"].fetch()
            repo.checkout_tree(repo.get('origin/main'))
            self.logger.info(f"Successfully updated repository: {url}")
        except Exception as e:
            self.logger.error(f"Failed to update repository {url}: {e}")
            raise e
        
    def get_repository_path(self, url: str) -> str:
        if url not in self.repos:
            raise ValueError(f"Repository not found at path: {self.repos[url]}")
        
        return self.repos[url]
    
    def complete_cleanup(self) -> None:
        for url, path in self.repos.items():
            try:    
                shutil.rmtree(path)
                self.logger.info(f"Cleaned up repository: {url} | at path: {path}")
            except Exception as e:
                self.logger.error(f"Error while cleaning up repository: {e}")
                raise e
            
        self.repos.clear()
                