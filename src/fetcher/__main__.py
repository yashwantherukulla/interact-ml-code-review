from .git_handler import GitHandler
from .repository_manager import RepositoryManager

def fetch_repository(url: str, base_path: str) -> str:
    git_handler = GitHandler()
    repo_manager = RepositoryManager(git_handler)

    repo_manager.clone_repository(url, base_path)


if __name__ == "__main__":
    url = "https://github.com/devHarshShah/techBarista"
    base_path = "./cloned_repos"
    
    git_handler = GitHandler()
    repo_manager = RepositoryManager(git_handler)
    fetch_repository(url, base_path)
    # repo_manager.complete_cleanup()