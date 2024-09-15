import pygit2
import logger
import os
import shutil


class GitHandler:
    def __init__(self):
        self.logger = logger.setupLogger()

    def clone_repository(self, url: str, path: str) -> pygit2.Repository:
        try:
            if os.path.exists(path):
                if os.path.exists(os.path.join(path, ".git")):
                    self.logger.info(f"Repository already exists at path: {path}")
                else:
                    self.logger.warning(
                        f"Directory exists but is not a Git repository: {path}"
                    )
                    shutil.rmtree(path)
            else:
                self.logger.info(f"Cloning repository to: {path}")
                pygit2.clone_repository(url, path)

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
