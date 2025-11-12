"""AI-powered commit summarization using OpenAI."""

import logging
from typing import Dict

import openai

from .git_utils import get_commit_diff

# Configure logging
logging.basicConfig(filename="changelog_errors.log", level=logging.ERROR)


def summarize_commit(commit, model: str, max_tokens: int = 300) -> str:
    """Generate a summary of a commit using OpenAI.

    Args:
        commit: GitPython commit object
        model: OpenAI model to use
        max_tokens: Maximum tokens for the summary

    Returns:
        AI-generated summary of the commit
    """
    commit_message = commit.message.strip()
    diff = get_commit_diff(commit)

    prompt = f"""
    You are an AI assistant creating a human-readable changelog.
    Analyze the following commit details:

    Commit Message:
    {commit_message}

    Code Changes:
    {diff[:3000]}  # Truncate large diffs for efficiency

    Provide a concise summary of the significant changes in plain language.
    """

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "Summarize code changes for changelogs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logging.error(f"Error summarizing commit {commit.hexsha[:7]}: {e}")
        return "Summary unavailable."


def generate_summaries(commits, model: str, max_tokens: int = 300, verbose: bool = False) -> Dict:
    """Generate summaries for multiple commits.

    Args:
        commits: List of GitPython commit objects
        model: OpenAI model to use
        max_tokens: Maximum tokens for each summary
        verbose: Show progress information

    Returns:
        Dictionary mapping commit hashes to summaries
    """
    from tqdm import tqdm
    from .git_utils import get_commit_info

    summaries = {}
    iterator = commits
    if verbose:
        iterator = tqdm(commits, desc="Generating summaries")

    for commit in iterator:
        info = get_commit_info(commit)
        summary = summarize_commit(commit, model, max_tokens)
        summaries[info["hash"]] = {
            **info,
            "summary": summary,
        }

    return summaries
