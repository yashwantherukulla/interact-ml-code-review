from .repo_ast import RepoAst
import os
import logging
from .ast_generator import AstGenerator

if __name__ == "__main__":
    cloneRepoPath = './cloned_repos'
    logger = logging.getLogger(__name__)
    ast_generator = AstGenerator()
    repo_ast = RepoAst(ast_generator)
    for repoFolder in os.listdir(cloneRepoPath):
        repoPath = os.path.join(cloneRepoPath, repoFolder)
        
        if os.path.isdir(repoPath):
            logger.info(f"Processing repository: {repoFolder}")
            repo_ast.processDirectory(repoPath)
        else:
            logger.info(f"Skipping non-directory item: {repoFolder}")