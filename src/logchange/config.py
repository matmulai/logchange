"""Configuration management for LogChange."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for changelog generation."""

    repo_path: str
    output_file: str
    max_commits: int
    model: str
    api_key: str
    output_format: str = "markdown"
    max_tokens: int = 300
    verbose: bool = False
    include_stats: bool = False

    @classmethod
    def from_args(cls, args) -> "Config":
        """Create config from parsed arguments."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key is not set. Please configure the 'OPENAI_API_KEY' environment variable."
            )

        return cls(
            repo_path=args.repo,
            output_file=args.output,
            max_commits=args.max_commits,
            model=args.model,
            api_key=api_key,
            output_format=args.format,
            max_tokens=args.max_tokens,
            verbose=args.verbose,
            include_stats=args.stats,
        )
