"""Generate AI-powered commit messages from git diffs."""

import argparse
import logging
import os
import sys

import git
from openai import OpenAI

# Configure logging
logging.basicConfig(filename="commit_msg_errors.log", level=logging.ERROR)


def parse_args() -> argparse.Namespace:
    """Return parsed command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate AI-powered commit messages from git diffs"
    )
    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--commit",
        help="Specific commit hash to generate message for (optional)",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Generate message for staged changes only",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4"),
        help="OpenAI model to use",
    )
    parser.add_argument(
        "--style",
        choices=["conventional", "concise", "detailed"],
        default="conventional",
        help="Commit message style (conventional, concise, or detailed)",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=72,
        help="Maximum length for commit message subject line",
    )
    return parser.parse_args()


def get_diff_content(repo, commit_hash=None, staged_only=False):
    """
    Get the diff content to analyze.
    """
    try:
        if commit_hash:
            # Get diff for specific commit
            commit = repo.commit(commit_hash)
            parent = commit.parents[0] if commit.parents else git.NULL_TREE
            diff = commit.diff(parent, create_patch=True)
            original_message = commit.message.strip()
        elif staged_only:
            # Get staged changes
            diff = repo.index.diff("HEAD", create_patch=True)
            original_message = None
        else:
            # Get all unstaged changes
            diff = repo.index.diff(None, create_patch=True)
            if not diff:
                # If no unstaged changes, check staged
                diff = repo.index.diff("HEAD", create_patch=True)
            original_message = None

        diff_text = "\n".join(
            d.diff.decode("utf-8", errors="ignore") for d in diff
        )

        if not diff_text.strip():
            return None, None, "No changes detected"

        return diff_text, original_message, None

    except Exception as e:
        return None, None, f"Error getting diff: {e}"


def generate_commit_message(client, model, diff_text, original_message, style, max_length):
    """
    Generate a commit message using OpenAI based on the diff.
    """
    style_instructions = {
        "conventional": """Follow Conventional Commits format:
<type>(<scope>): <subject>

<body>

<footer>

Types: feat, fix, docs, style, refactor, test, chore
Subject: imperative mood, no period, max {max_length} chars
Body: explain what and why (optional)
Footer: breaking changes, issue references (optional)""",
        "concise": """Generate a single-line commit message that:
- Is concise and under {max_length} characters
- Uses imperative mood (e.g., "Add feature" not "Added feature")
- Clearly describes what changed""",
        "detailed": """Generate a detailed commit message with:
- Subject line (max {max_length} chars, imperative mood)
- Blank line
- Detailed body explaining what changed and why
- Any relevant technical details""",
    }

    style_instruction = style_instructions[style].format(max_length=max_length)

    prompt = f"""Generate a commit message for the following code changes.

{style_instruction}

Code Changes:
{diff_text[:4000]}  # Truncate for efficiency
"""

    if original_message:
        prompt += f"\n\nOriginal commit message (for reference):\n{original_message}\n"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at writing clear, concise commit messages. "
                    "Generate only the commit message, no extra commentary.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error generating commit message: {e}")
        return None


def main() -> None:
    args = parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(
            "Error: OpenAI API key is not set. "
            "Please configure the 'OPENAI_API_KEY' environment variable.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        repo = git.Repo(args.repo)
    except git.exc.InvalidGitRepositoryError:
        print(f"Error: '{args.repo}' is not a valid git repository", file=sys.stderr)
        sys.exit(1)

    # Get diff content
    diff_text, original_message, error = get_diff_content(
        repo, args.commit, args.staged
    )

    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if not diff_text:
        print("No changes to generate commit message for", file=sys.stderr)
        sys.exit(1)

    # Generate commit message
    client = OpenAI(api_key=api_key)
    commit_message = generate_commit_message(
        client, args.model, diff_text, original_message, args.style, args.max_length
    )

    if not commit_message:
        print("Error: Failed to generate commit message", file=sys.stderr)
        sys.exit(1)

    # Output the generated commit message
    print(commit_message)

    if original_message:
        print("\n" + "=" * 50)
        print("Original message:")
        print(original_message)


if __name__ == "__main__":
    main()
