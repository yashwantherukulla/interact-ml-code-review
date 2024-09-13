from .chunker2.chunk_extractor import ChunkExtractor2
from .code_analyser.code_analyser import CodeAnalyser
from .fetcher.git_handler import GitHandler
from .fetcher.repository_manager import RepositoryManager


def fetch_repository(url: str, base_path: str) -> str:
    git_handler = GitHandler()
    repo_manager = RepositoryManager(git_handler)

    repo_manager.clone_repository(url, base_path)

if __name__ == "__main__":
    cloneRepoPath = "./cloned_repos"
    
    #repo to clone here
    url = "https://github.com/kiwi0fruit/ipynb-py-convert.git"

    chunk_extractor = ChunkExtractor2()
    code_analyser = CodeAnalyser()
    git_handler = GitHandler()
    repo_manager = RepositoryManager(git_handler)
    fetch_repository(url, cloneRepoPath)
    # repo_manager.complete_cleanup()
    chunk_extractor.processRepos(cloneRepoPath)
    code_analyser.processRepos(cloneRepoPath)