import os
import git
from pathlib import Path

def get_repo_root() -> str:
    """ Get the top-level directory in this repository

    Returns:
        str -- Absolute path to directory
    """
    git_repo = git.Repo(Path(__file__).absolute(), search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return os.path.abspath(git_root)


def join_from_repo_root(*paths) -> str:
    """ os.path.join from the repository root """
    return os.path.join(get_repo_root(), *paths)
