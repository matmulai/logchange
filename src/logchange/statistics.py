"""Statistics collection for changelog generation."""

from typing import List, Dict, Any
from collections import Counter


def calculate_statistics(changelog: List[Dict[str, Any]], model: str) -> Dict[str, Any]:
    """Calculate statistics from changelog data.

    Args:
        changelog: List of changelog entries
        model: Model used for generation

    Returns:
        Dictionary containing statistics
    """
    if not changelog:
        return {
            "total_commits": 0,
            "contributors": 0,
            "date_range": "N/A",
            "model": model,
        }

    dates = [entry['date'] for entry in changelog]
    authors = [entry.get('author', 'Unknown') for entry in changelog]
    author_counts = Counter(authors)

    stats = {
        "total_commits": len(changelog),
        "contributors": len(author_counts),
        "date_range": f"{min(dates)} to {max(dates)}",
        "model": model,
        "top_contributors": dict(author_counts.most_common(5)),
        "commits_by_date": dict(Counter(dates)),
    }

    return stats
