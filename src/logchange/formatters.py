"""Output formatters for changelog generation."""

import json
import csv
from typing import List, Dict, Any
from datetime import datetime


class ChangelogFormatter:
    """Base class for changelog formatters."""

    def format(self, changelog: List[Dict[str, Any]], stats: Dict[str, Any] = None) -> str:
        """Format changelog data."""
        raise NotImplementedError


class MarkdownFormatter(ChangelogFormatter):
    """Markdown output formatter."""

    def format(self, changelog: List[Dict[str, Any]], stats: Dict[str, Any] = None) -> str:
        """Format changelog as markdown.

        Args:
            changelog: List of changelog entries
            stats: Optional statistics to include

        Returns:
            Formatted markdown string
        """
        lines = ["# Changelog\n"]

        if stats:
            lines.append("## Statistics\n")
            lines.append(f"- Total commits: {stats.get('total_commits', 0)}")
            lines.append(f"- Date range: {stats.get('date_range', 'N/A')}")
            lines.append(f"- Contributors: {stats.get('contributors', 0)}")
            lines.append(f"- Model used: {stats.get('model', 'N/A')}\n")

        current_date = None
        for entry in changelog:
            if entry['date'] != current_date:
                current_date = entry['date']
                lines.append(f"## {current_date}\n")

            lines.append(f"### {entry['hash']}")
            lines.append(f"**Author:** {entry.get('author', 'Unknown')}")
            lines.append(f"**Commit Message:** {entry['message']}\n")
            lines.append(f"**AI Summary:** {entry['summary']}\n")

        return "\n".join(lines)


class JSONFormatter(ChangelogFormatter):
    """JSON output formatter."""

    def format(self, changelog: List[Dict[str, Any]], stats: Dict[str, Any] = None) -> str:
        """Format changelog as JSON.

        Args:
            changelog: List of changelog entries
            stats: Optional statistics to include

        Returns:
            Formatted JSON string
        """
        output = {
            "generated_at": datetime.now().isoformat(),
            "changelog": changelog,
        }

        if stats:
            output["statistics"] = stats

        return json.dumps(output, indent=2)


class CSVFormatter(ChangelogFormatter):
    """CSV output formatter."""

    def format(self, changelog: List[Dict[str, Any]], stats: Dict[str, Any] = None) -> str:
        """Format changelog as CSV.

        Args:
            changelog: List of changelog entries
            stats: Optional statistics to include

        Returns:
            Formatted CSV string
        """
        import io

        output = io.StringIO()
        if changelog:
            fieldnames = ['hash', 'date', 'author', 'message', 'summary']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for entry in changelog:
                writer.writerow({
                    'hash': entry.get('hash', ''),
                    'date': entry.get('date', ''),
                    'author': entry.get('author', ''),
                    'message': entry.get('message', ''),
                    'summary': entry.get('summary', ''),
                })

        return output.getvalue()


def get_formatter(format_type: str) -> ChangelogFormatter:
    """Get the appropriate formatter for the given format type.

    Args:
        format_type: Type of formatter (markdown, json, csv)

    Returns:
        Formatter instance
    """
    formatters = {
        "markdown": MarkdownFormatter(),
        "json": JSONFormatter(),
        "csv": CSVFormatter(),
    }

    formatter = formatters.get(format_type.lower())
    if not formatter:
        raise ValueError(f"Unknown format: {format_type}. Choose from: {', '.join(formatters.keys())}")

    return formatter


def write_output(content: str, output_file: str) -> None:
    """Write formatted content to a file.

    Args:
        content: Formatted changelog content
        output_file: Path to output file
    """
    with open(output_file, "w") as f:
        f.write(content)
