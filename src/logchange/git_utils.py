"""Git repository operations."""

from datetime import datetime
from typing import List, Dict

import git
from git import NULL_TREE
from tqdm import tqdm


def get_commit_info(commit) -> Dict[str, str]:
    """Extract information from a git commit.

    Args:
        commit: GitPython commit object

    Returns:
        Dictionary containing commit information
    """
    return {
        "hash": commit.hexsha[:7],
        "full_hash": commit.hexsha,
        "message": commit.message.strip(),
        "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d'),
        "author": commit.author.name,
        "email": commit.author.email,
    }


def get_commit_diff(commit) -> str:
    """Get the diff for a commit.

    Args:
        commit: GitPython commit object

    Returns:
        String containing the commit diff
    """
    parent = commit.parents[0] if commit.parents else NULL_TREE
    diff = "\n".join(
        d.diff.decode("utf-8", errors="ignore")
        for d in commit.diff(parent, create_patch=True)
    )
    return diff


def iterate_commits(repo_path: str, max_commits: int, verbose: bool = False) -> List[git.Commit]:
    """Iterate through commits in a repository.

    Args:
        repo_path: Path to the git repository
        max_commits: Maximum number of commits to retrieve
        verbose: Show progress bar

    Returns:
        List of commit objects
    """
    repo = git.Repo(repo_path)
    commits = []

    iterator = repo.iter_commits(max_count=max_commits)
    if verbose:
        iterator = tqdm(iterator, desc="Fetching commits", total=max_commits)

    for commit in iterator:
        commits.append(commit)

    return commits
