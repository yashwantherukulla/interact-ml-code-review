from .chunker2.chunk_extractor import ChunkExtractor2
from .code_analyser.code_analyser import CodeAnalyser
from .fetcher.git_handler import GitHandler
from .fetcher.repository_manager import RepositoryManager
import logging

def fetch_repository(url: str, base_path: str) -> str:
    git_handler = GitHandler()
    repo_manager = RepositoryManager(git_handler)
    
    repo_manager.clone_repository(url, base_path)

def main(repos):
    logger = logging.getLogger(__name__)
    if repos != []:
        repos = repos[1:len(repos)-1].split(' ')
    else:
        logger.info("Please provide a repository URL")

    cloneRepoPath = "./cloned_repos"

    chunk_extractor = ChunkExtractor2()
    code_analyser = CodeAnalyser()
    git_handler = GitHandler()
    repo_manager = RepositoryManager(git_handler)

    for repo in repos:
        fetch_repository(repo, cloneRepoPath)
    
    repo_manager.complete_cleanup()
    chunk_extractor.processRepos(cloneRepoPath)
    code_analyser.processRepos(cloneRepoPath)