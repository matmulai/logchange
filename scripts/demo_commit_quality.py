#!/usr/bin/env python3
"""
Demo script to compare AI-generated commit messages with actual messages.
This demonstrates the quality of the commit message generator.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

import git
from gen_commit_msg import generate_commit_message, get_diff_content
from openai import OpenAI


def get_recent_commits(repo, count=5):
    """Get recent commits with their diffs."""
    commits = []
    for commit in repo.iter_commits(max_count=count):
        commits.append(commit)
    return commits


def generate_comparison_report(repo_path=".", num_commits=5):
    """Generate a comparison report of AI vs actual commit messages."""

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("\nTo use this demo, please:")
        print("1. Get an OpenAI API key from https://platform.openai.com/api-keys")
        print("2. Export it: export OPENAI_API_KEY=sk-your-key")
        print("3. Run this script again")
        return None

    try:
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        print(f"Error: '{repo_path}' is not a valid git repository")
        return None

    commits = get_recent_commits(repo, num_commits)
    client = OpenAI(api_key=api_key)

    print("=" * 80)
    print("LOGCHANGE COMMIT MESSAGE QUALITY ASSESSMENT")
    print("=" * 80)
    print()
    print(f"Analyzing {len(commits)} recent commits...\n")

    results = []

    for i, commit in enumerate(commits, 1):
        print(f"[{i}/{len(commits)}] Processing commit {commit.hexsha[:7]}...")

        # Get diff for this commit
        parent = commit.parents[0] if commit.parents else git.NULL_TREE
        diff = commit.diff(parent, create_patch=True)
        diff_text = "\n".join(
            d.diff.decode("utf-8", errors="ignore") for d in diff
        )

        # Generate AI messages in different styles
        ai_messages = {}
        for style in ["conventional", "concise", "detailed"]:
            print(f"  Generating {style} style message...")
            ai_msg = generate_commit_message(
                client,
                "gpt-4",
                diff_text,
                None,  # Don't show original message to AI
                style,
                72,
                cache=None,  # Disable cache for demo
                rate_limiter=None,
            )
            ai_messages[style] = ai_msg if ai_msg else "Generation failed"

        results.append({
            "hash": commit.hexsha[:7],
            "actual": commit.message.strip(),
            "ai_messages": ai_messages,
            "author": commit.author.name,
            "date": commit.committed_datetime.strftime("%Y-%m-%d %H:%M"),
        })

    return results


def save_report_to_file(results, output_file="COMMIT_QUALITY_REPORT.md"):
    """Save the comparison report to a markdown file."""

    with open(output_file, "w") as f:
        f.write("# Commit Message Quality Assessment Report\n\n")
        f.write("This report compares actual commit messages with AI-generated messages using LogChange.\n\n")
        f.write(f"**Total Commits Analyzed:** {len(results)}\n\n")
        f.write("---\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"## Commit {i}: `{result['hash']}`\n\n")
            f.write(f"**Author:** {result['author']}  \n")
            f.write(f"**Date:** {result['date']}\n\n")

            f.write("### Actual Commit Message\n")
            f.write("```\n")
            f.write(result['actual'])
            f.write("\n```\n\n")

            f.write("### AI-Generated Messages\n\n")

            for style, message in result['ai_messages'].items():
                f.write(f"#### Style: `{style}`\n")
                f.write("```\n")
                f.write(message)
                f.write("\n```\n\n")

            f.write("### Assessment\n\n")
            f.write("| Criteria | Actual | AI (Conventional) | Notes |\n")
            f.write("|----------|--------|-------------------|-------|\n")
            f.write("| Clarity | - | - | *Your assessment here* |\n")
            f.write("| Completeness | - | - | *Your assessment here* |\n")
            f.write("| Style Consistency | - | - | *Your assessment here* |\n\n")

            f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write("### Observations\n\n")
        f.write("- **Strengths of AI-generated messages:**\n")
        f.write("  - (Add your observations)\n\n")
        f.write("- **Strengths of actual messages:**\n")
        f.write("  - (Add your observations)\n\n")
        f.write("- **Areas for improvement:**\n")
        f.write("  - (Add your observations)\n\n")

    print(f"\n✓ Report saved to: {output_file}")


def main():
    """Main entry point."""

    print("LogChange Commit Message Quality Demo")
    print("=" * 80)
    print()

    results = generate_comparison_report()

    if results:
        print("\n" + "=" * 80)
        print("PREVIEW OF RESULTS")
        print("=" * 80 + "\n")

        for result in results[:2]:  # Show first 2 as preview
            print(f"Commit: {result['hash']}")
            print(f"Actual: {result['actual'][:60]}...")
            print(f"AI (Conventional): {result['ai_messages']['conventional'][:60]}...")
            print()

        save_report_to_file(results)

        print("\n" + "=" * 80)
        print("SUCCESS! Review COMMIT_QUALITY_REPORT.md for full comparison")
        print("=" * 80)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
