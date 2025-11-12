"""Command-line interface for LogChange."""

import argparse
import os
import sys

import openai

from .config import Config
from .git_utils import iterate_commits, get_commit_info
from .ai_summarizer import summarize_commit
from .formatters import get_formatter, write_output
from .statistics import calculate_statistics


def parse_args() -> argparse.Namespace:
    """Return parsed command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate an AI-powered changelog from git commits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate markdown changelog with default settings
  %(prog)s

  # Generate JSON changelog with statistics
  %(prog)s --format json --stats --output changelog.json

  # Generate changelog for last 100 commits using GPT-4
  %(prog)s --max-commits 100 --model gpt-4 --verbose

  # Generate CSV format for data analysis
  %(prog)s --format csv --output results.csv --stats
        """
    )

    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--output",
        default="changelog.md",
        help="File to write changelog to (default: changelog.md)",
    )
    parser.add_argument(
        "--max-commits",
        type=int,
        default=50,
        help="Number of recent commits to include (default: 50)",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", "gpt-4"),
        help="OpenAI model to use (default: gpt-4, or OPENAI_MODEL env var)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "csv"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=300,
        help="Maximum tokens per summary (default: 300)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show progress information",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Include statistics in output",
    )

    return parser.parse_args()


def generate_changelog(config: Config) -> None:
    """Generate changelog based on configuration.

    Args:
        config: Configuration object
    """
    # Set OpenAI API key
    openai.api_key = config.api_key

    # Fetch commits
    if config.verbose:
        print(f"Fetching up to {config.max_commits} commits from {config.repo_path}...")

    commits = iterate_commits(config.repo_path, config.max_commits, config.verbose)

    if not commits:
        print("No commits found.", file=sys.stderr)
        sys.exit(1)

    # Generate changelog entries
    if config.verbose:
        print(f"Generating summaries using {config.model}...")

    changelog = []
    for i, commit in enumerate(commits, 1):
        if config.verbose:
            print(f"Processing commit {i}/{len(commits)}: {commit.hexsha[:7]}", end="\r")

        info = get_commit_info(commit)
        summary = summarize_commit(commit, config.model, config.max_tokens)
        changelog.append({
            **info,
            "summary": summary,
        })

    if config.verbose:
        print()  # New line after progress

    # Calculate statistics if requested
    stats = None
    if config.include_stats:
        stats = calculate_statistics(changelog, config.model)
        if config.verbose:
            print("\nStatistics:")
            print(f"  Total commits: {stats['total_commits']}")
            print(f"  Contributors: {stats['contributors']}")
            print(f"  Date range: {stats['date_range']}")
            print(f"  Model: {stats['model']}")

    # Format and write output
    formatter = get_formatter(config.output_format)
    content = formatter.format(changelog, stats)
    write_output(content, config.output_file)

    print(f"\n✓ Changelog generated and saved to '{config.output_file}'")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        args = parse_args()
        config = Config.from_args(args)
        generate_changelog(config)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
