import logging
import os
import subprocess
from collections import namedtuple
from functools import lru_cache

logger = logging.getLogger(__name__)


class GitManager(namedtuple("GitManager", ["git_dir", "work_dir"])):
    @property
    @lru_cache(None)
    def env(self):
        git_dir = self.git_dir
        if git_dir is None:
            git_dir = "/run/turingarena/db.git"

        logger.info(f"Using git repository at {git_dir}")
        author_name = "TuringArena"
        author_email = "contact@turingarena.org"
        return {
            "GIT_DIR": git_dir,
            "GIT_WORK_TREE": self.work_dir,
            "GIT_AUTHOR_NAME": author_name,
            "GIT_AUTHOR_EMAIL": author_email,
            "GIT_COMMITTER_NAME": author_name,
            "GIT_COMMITTER_EMAIL": author_email,
        }

    def fetch_repositories(self, repositories):
        for repository in repositories:
            # TODO: add a way to specify branch and depth
            logger.info(f"Fetching git repository {repository}")
            subprocess.call(["git", "fetch", "--recurse-submodules=yes", repository], env=self.env)

    def import_trees(self, tree_ids):
        for tree_id in tree_ids:
            logger.info(f"Importing git tree id {tree_id}")
            subprocess.call(["git", "read-tree", tree_id], env=self.env)
            subprocess.call(["git", "checkout-index", "--all"], env=self.env)

    def receive_current_directory(self, current_dir, tree_id):
        logger.info("Retriving current directory from git")

        self.import_trees([tree_id])

        if current_dir:
            os.chdir(current_dir)

    def add_directory(self, directory):
        logger.info(f"Add directory {directory} to be committed")
        subprocess.call(["git", "add", "-A", directory], env=self.env)

    def commit_work(self):
        logger.info("Committing work")

        tree_id = subprocess.check_output(["git", "write-tree"], env=self.env).strip().decode("ascii")
        logger.info(f"Output written with tree-id {tree_id}")

        commit_id = subprocess.check_output(["git", "commit-tree", tree_id, "-m", "Make output"],
                                            env=self.env).strip().decode("ascii")
        logger.info(f"Created commit with commit-id {commit_id}")

        return tree_id, commit_id
