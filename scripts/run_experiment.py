#!/usr/bin/env python3
"""Experiment runner for testing different LogChange configurations.

This script runs multiple changelog generation experiments with different
configurations and collects results for comparison.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import openai
from logchange.config import Config
from logchange.git_utils import iterate_commits, get_commit_info
from logchange.ai_summarizer import summarize_commit
from logchange.statistics import calculate_statistics


class ExperimentConfig:
    """Configuration for an experiment run."""

    def __init__(self, name: str, model: str, max_commits: int = 10, max_tokens: int = 300):
        self.name = name
        self.model = model
        self.max_commits = max_commits
        self.max_tokens = max_tokens


def run_single_experiment(exp_config: ExperimentConfig, repo_path: str, api_key: str) -> Dict[str, Any]:
    """Run a single experiment with the given configuration.

    Args:
        exp_config: Experiment configuration
        repo_path: Path to git repository
        api_key: OpenAI API key

    Returns:
        Dictionary containing experiment results
    """
    openai.api_key = api_key

    print(f"\n{'='*60}")
    print(f"Running experiment: {exp_config.name}")
    print(f"Model: {exp_config.model}, Commits: {exp_config.max_commits}, Max tokens: {exp_config.max_tokens}")
    print(f"{'='*60}")

    # Fetch commits
    commits = iterate_commits(repo_path, exp_config.max_commits, verbose=False)

    # Generate summaries
    changelog = []
    start_time = datetime.now()

    for i, commit in enumerate(commits, 1):
        print(f"Processing commit {i}/{len(commits)}: {commit.hexsha[:7]}", end="\r")
        info = get_commit_info(commit)
        summary = summarize_commit(commit, exp_config.model, exp_config.max_tokens)
        changelog.append({
            **info,
            "summary": summary,
        })

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print()  # New line after progress

    # Calculate statistics
    stats = calculate_statistics(changelog, exp_config.model)
    stats['duration_seconds'] = duration
    stats['avg_time_per_commit'] = duration / len(commits) if commits else 0

    print(f"✓ Completed in {duration:.2f} seconds ({stats['avg_time_per_commit']:.2f}s per commit)")

    return {
        "experiment_name": exp_config.name,
        "config": {
            "model": exp_config.model,
            "max_commits": exp_config.max_commits,
            "max_tokens": exp_config.max_tokens,
        },
        "statistics": stats,
        "changelog": changelog,
    }


def compare_results(results: List[Dict[str, Any]]) -> str:
    """Generate a comparison report of experiment results.

    Args:
        results: List of experiment results

    Returns:
        Formatted comparison report
    """
    lines = ["\n" + "="*80]
    lines.append("EXPERIMENT COMPARISON REPORT")
    lines.append("="*80 + "\n")

    # Summary table
    lines.append("Summary:")
    lines.append("-" * 80)
    lines.append(f"{'Experiment':<30} {'Model':<15} {'Commits':<10} {'Duration':<12} {'Avg/Commit'}")
    lines.append("-" * 80)

    for result in results:
        name = result['experiment_name']
        model = result['config']['model']
        commits = result['statistics']['total_commits']
        duration = result['statistics']['duration_seconds']
        avg = result['statistics']['avg_time_per_commit']

        lines.append(f"{name:<30} {model:<15} {commits:<10} {duration:>8.2f}s    {avg:>6.2f}s")

    lines.append("-" * 80 + "\n")

    # Detailed statistics
    lines.append("Detailed Statistics:")
    lines.append("-" * 80)

    for result in results:
        lines.append(f"\n{result['experiment_name']}:")
        stats = result['statistics']
        lines.append(f"  Model: {stats['model']}")
        lines.append(f"  Total commits: {stats['total_commits']}")
        lines.append(f"  Contributors: {stats['contributors']}")
        lines.append(f"  Date range: {stats['date_range']}")
        lines.append(f"  Duration: {stats['duration_seconds']:.2f}s")
        lines.append(f"  Avg time per commit: {stats['avg_time_per_commit']:.2f}s")

        if 'top_contributors' in stats:
            lines.append(f"  Top contributors: {', '.join(list(stats['top_contributors'].keys())[:3])}")

    lines.append("\n" + "="*80)

    return "\n".join(lines)


def save_results(results: List[Dict[str, Any]], output_dir: str) -> None:
    """Save experiment results to files.

    Args:
        results: List of experiment results
        output_dir: Directory to save results
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save full results as JSON
    results_file = os.path.join(output_dir, "experiment_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "experiments": results,
        }, f, indent=2)

    print(f"\n✓ Full results saved to: {results_file}")

    # Save comparison report
    report_file = os.path.join(output_dir, "comparison_report.txt")
    with open(report_file, 'w') as f:
        f.write(compare_results(results))

    print(f"✓ Comparison report saved to: {report_file}")

    # Save individual changelogs
    for result in results:
        exp_name = result['experiment_name'].replace(' ', '_').lower()
        changelog_file = os.path.join(output_dir, f"changelog_{exp_name}.md")

        with open(changelog_file, 'w') as f:
            f.write(f"# Changelog - {result['experiment_name']}\n\n")
            f.write(f"**Model:** {result['config']['model']}\n")
            f.write(f"**Duration:** {result['statistics']['duration_seconds']:.2f}s\n\n")

            for entry in result['changelog']:
                f.write(f"## {entry['date']} - {entry['hash']}\n")
                f.write(f"**Author:** {entry['author']}\n")
                f.write(f"**Message:** {entry['message']}\n\n")
                f.write(f"**Summary:** {entry['summary']}\n\n")

        print(f"✓ Changelog saved to: {changelog_file}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run LogChange experiments with different configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run quick experiment with default models
  %(prog)s --quick

  # Run full experiment comparing multiple models
  %(prog)s --models gpt-3.5-turbo gpt-4 --max-commits 20

  # Run custom experiments
  %(prog)s --custom '{"name": "Test", "model": "gpt-4", "max_commits": 5}'
        """
    )

    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Path to git repository (default: current directory)",
    )
    parser.add_argument(
        "--output-dir",
        default="experiment_results",
        help="Directory to save results (default: experiment_results)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick experiment (5 commits, gpt-3.5-turbo)",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        help="Models to test (e.g., gpt-3.5-turbo gpt-4)",
    )
    parser.add_argument(
        "--max-commits",
        type=int,
        default=10,
        help="Number of commits to process (default: 10)",
    )
    parser.add_argument(
        "--custom",
        type=str,
        help="Custom experiment config as JSON string",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Configure experiments
    experiments = []

    if args.quick:
        experiments.append(ExperimentConfig("Quick Test", "gpt-3.5-turbo", 5, 200))
    elif args.custom:
        config_data = json.loads(args.custom)
        experiments.append(ExperimentConfig(
            config_data.get("name", "Custom"),
            config_data["model"],
            config_data.get("max_commits", 10),
            config_data.get("max_tokens", 300),
        ))
    elif args.models:
        for model in args.models:
            experiments.append(ExperimentConfig(
                f"Test: {model}",
                model,
                args.max_commits,
                300,
            ))
    else:
        # Default experiments
        experiments = [
            ExperimentConfig("GPT-3.5 Turbo", "gpt-3.5-turbo", args.max_commits, 300),
            ExperimentConfig("GPT-4", "gpt-4", args.max_commits, 300),
        ]

    print(f"Running {len(experiments)} experiment(s)...")

    # Run experiments
    results = []
    for exp_config in experiments:
        try:
            result = run_single_experiment(exp_config, args.repo, api_key)
            results.append(result)
        except Exception as e:
            print(f"Error in experiment '{exp_config.name}': {e}", file=sys.stderr)
            continue

    if not results:
        print("No experiments completed successfully", file=sys.stderr)
        sys.exit(1)

    # Display and save results
    print(compare_results(results))
    save_results(results, args.output_dir)

    print(f"\n✓ All experiments completed! Results saved to: {args.output_dir}/")


if __name__ == "__main__":
    main()
