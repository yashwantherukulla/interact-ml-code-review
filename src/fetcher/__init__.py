from .git_handler import GitHandler
from .repository_manager import RepositoryManager

__all__ = ["GitHandler", "RepositoryManager"]

def fetch_repository(url: str, base_path: str) -> str:
    git_handler = GitHandler()
    repo_manager = RepositoryManager(git_handler)

    repo_manager.clone_repository(url, base_path)
    