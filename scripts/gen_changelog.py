"""Generate a commit changelog using OpenAI."""

import argparse
import logging
import os
from datetime import datetime

import git
from git import NULL_TREE
from openai import OpenAI
from tqdm import tqdm

# Configure logging
logging.basicConfig(filename="changelog_errors.log", level=logging.ERROR)


def parse_args() -> argparse.Namespace:
    """Return parsed command line arguments."""
    parser = argparse.ArgumentParser(description="Generate an AI-powered changelog")
    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--output",
        default="changelog.md",
        help="Markdown file to write changelog to",
    )
    parser.add_argument(
        "--max-commits",
        type=int,
        default=50,
        help="Number of recent commits to include",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4"),
        help="OpenAI model to use",
    )
    return parser.parse_args()

def summarize_commit(commit, client, model, max_tokens=300):
    """
    Generate a summary of a commit using OpenAI.
    """
    commit_message = commit.message.strip()
    parent = commit.parents[0] if commit.parents else NULL_TREE

    try:
        diff = "\n".join(
            d.diff.decode("utf-8", errors="ignore")
            for d in commit.diff(parent, create_patch=True)
        )
    except Exception as e:
        logging.error(f"Error getting diff for commit {commit.hexsha[:7]}: {e}")
        diff = ""

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
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Summarize code changes for changelogs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error summarizing commit {commit.hexsha[:7]}: {e}")
        return "Summary unavailable."

def generate_changelog(repo, client, model, max_commits=50):
    """
    Generate a changelog with OpenAI-generated summaries.
    """
    changelog = []
    for commit in tqdm(repo.iter_commits(max_count=max_commits), desc="Processing commits"):
        summary = summarize_commit(commit, client, model)
        changelog.append({
            "hash": commit.hexsha[:7],
            "message": commit.message.strip(),
            "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d'),
            "summary": summary,
        })
    return changelog

def write_changelog_to_markdown(changelog, output_file: str) -> None:
    """
    Write the changelog to a markdown file.
    """
    with open(output_file, "w") as f:
        f.write("# Changelog\n\n")
        current_date = None
        for entry in changelog:
            if entry['date'] != current_date:
                current_date = entry['date']
                f.write(f"## {current_date}\n\n")
            f.write(f"### {entry['hash']}\n")
            f.write(f"**Commit Message:** {entry['message']}\n\n")
            f.write(f"**AI Summary:** {entry['summary']}\n\n")

def main() -> None:
    args = parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key is not set. Please configure the 'OPENAI_API_KEY' environment variable."
        )

    client = OpenAI(api_key=api_key)
    repo = git.Repo(args.repo)
    changelog = generate_changelog(repo, client, args.model, max_commits=args.max_commits)
    write_changelog_to_markdown(changelog, args.output)
    print(f"Changelog generated and saved to '{args.output}'")


if __name__ == "__main__":
    main()
