# LogChange: GenAI Assisted Changelog Generation

LogChange generates project changelogs by summarizing git commits using OpenAI's language models. It provides a convenient way to automatically create human-readable changelogs from your commit history.

## Features

- 🤖 **AI-Powered Summaries**: Uses OpenAI models to generate concise, readable commit summaries
- 📊 **Multiple Output Formats**: Supports Markdown, JSON, and CSV formats
- 📈 **Statistics**: Optional statistics including contributor counts, date ranges, and more
- 🎯 **Experiment Runner**: Compare different models and configurations
- 🔧 **Highly Configurable**: Customize models, token limits, commit ranges, and more
- 🚀 **GitHub Actions Integration**: Automated changelog generation on push

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/matmulai/logchange.git
cd logchange

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here
```

### Install as Package (Optional)

```bash
pip install -e .
```

This makes the `logchange` command available globally.

## Requirements

- Python 3.8+
- OpenAI API key
- Git repository

## Usage

### Basic Usage

Generate a markdown changelog from the current repository:

```bash
python logchange.py
```

This creates a `changelog.md` file with summaries of the last 50 commits.

### Command-Line Options

```bash
python logchange.py [OPTIONS]
```

**Options:**

- `--repo PATH` - Path to git repository (default: current directory)
- `--output FILE` - Output file path (default: changelog.md)
- `--max-commits N` - Number of commits to process (default: 50)
- `--model MODEL` - OpenAI model to use (default: gpt-4)
- `--format FORMAT` - Output format: markdown, json, or csv (default: markdown)
- `--max-tokens N` - Maximum tokens per summary (default: 300)
- `--verbose` - Show progress information
- `--stats` - Include statistics in output

### Examples

#### Generate JSON output with statistics

```bash
python logchange.py --format json --stats --output changelog.json
```

#### Use GPT-3.5 Turbo for faster/cheaper generation

```bash
python logchange.py --model gpt-3.5-turbo --max-commits 100 --verbose
```

#### Generate CSV for data analysis

```bash
python logchange.py --format csv --output results.csv --max-commits 200
```

#### Process a different repository

```bash
python logchange.py --repo /path/to/other/repo --output other-changelog.md
```

## Running Experiments

The experiment runner allows you to compare different models and configurations:

### Quick Test

Run a quick experiment with 5 commits using GPT-3.5 Turbo:

```bash
python scripts/run_experiment.py --quick
```

### Compare Multiple Models

Compare GPT-3.5 Turbo and GPT-4 on the same commits:

```bash
python scripts/run_experiment.py --models gpt-3.5-turbo gpt-4 --max-commits 20
```

### Custom Experiment

Run a custom experiment with specific configuration:

```bash
python scripts/run_experiment.py --custom '{"name": "My Test", "model": "gpt-4", "max_commits": 15, "max_tokens": 200}'
```

### Experiment Options

- `--repo PATH` - Repository to analyze (default: current directory)
- `--output-dir DIR` - Directory for results (default: experiment_results)
- `--quick` - Quick test with 5 commits
- `--models MODEL [MODEL ...]` - List of models to compare
- `--max-commits N` - Commits per experiment (default: 10)
- `--custom JSON` - Custom experiment configuration

### Experiment Output

The experiment runner generates:

1. **experiment_results.json** - Full results in JSON format
2. **comparison_report.txt** - Human-readable comparison report
3. **changelog_*.md** - Individual changelogs for each experiment

Example output structure:

```
experiment_results/
├── experiment_results.json
├── comparison_report.txt
├── changelog_gpt-3.5_turbo.md
└── changelog_gpt-4.md
```

### Sample Comparison Report

```
================================================================================
EXPERIMENT COMPARISON REPORT
================================================================================

Summary:
--------------------------------------------------------------------------------
Experiment                     Model           Commits    Duration     Avg/Commit
--------------------------------------------------------------------------------
GPT-3.5 Turbo                  gpt-3.5-turbo   10           12.45s      1.25s
GPT-4                          gpt-4           10           23.67s      2.37s
--------------------------------------------------------------------------------
```

## Output Formats

### Markdown (Default)

Human-readable changelog with dates, commits, and AI summaries:

```markdown
# Changelog

## 2024-01-15

### abc1234
**Author:** John Doe
**Commit Message:** Add new feature

**AI Summary:** Implemented a new authentication system...
```

### JSON

Structured data perfect for programmatic processing:

```json
{
  "generated_at": "2024-01-15T10:30:00",
  "statistics": {
    "total_commits": 50,
    "contributors": 5,
    "date_range": "2024-01-01 to 2024-01-15"
  },
  "changelog": [
    {
      "hash": "abc1234",
      "date": "2024-01-15",
      "author": "John Doe",
      "message": "Add new feature",
      "summary": "Implemented a new authentication system..."
    }
  ]
}
```

### CSV

Tabular format for spreadsheet analysis:

```csv
hash,date,author,message,summary
abc1234,2024-01-15,John Doe,Add new feature,Implemented a new authentication system...
```

## GitHub Actions Integration

The repository includes a GitHub Actions workflow that automatically generates changelogs:

```yaml
# .github/workflows/changelog.yml
name: Generate AI-Powered Changelog

on:
  workflow_dispatch:  # Manual trigger
  push:
    branches:
      - main
```

**Setup:**

1. Add your OpenAI API key as a repository secret named `OPENAI_API_KEY`
2. The workflow runs automatically on pushes to main
3. Download the generated changelog from the Actions artifacts

## Configuration

### Environment Variables

- `OPENAI_API_KEY` (required) - Your OpenAI API key
- `OPENAI_MODEL` (optional) - Default model to use (default: gpt-4)

### Model Selection

Common OpenAI models:

- `gpt-4` - Most capable, slower, more expensive
- `gpt-4-turbo` - Faster GPT-4 variant
- `gpt-3.5-turbo` - Fast and cost-effective
- `gpt-3.5-turbo-16k` - Extended context window

## Project Structure

```
logchange/
├── src/
│   └── logchange/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Command-line interface
│       ├── config.py            # Configuration management
│       ├── git_utils.py         # Git operations
│       ├── ai_summarizer.py     # OpenAI integration
│       ├── formatters.py        # Output formatters
│       └── statistics.py        # Statistics calculation
├── scripts/
│   ├── gen_changelog.py         # Legacy script (deprecated)
│   └── run_experiment.py        # Experiment runner
├── .github/
│   └── workflows/
│       └── changelog.yml        # GitHub Actions workflow
├── logchange.py                 # Main entry point
├── pyproject.toml              # Package configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Troubleshooting

### API Key Issues

```bash
# Verify your API key is set
echo $OPENAI_API_KEY

# Set it if not configured
export OPENAI_API_KEY=sk-your-key-here
```

### Rate Limiting

If you encounter rate limits:

- Use `--max-commits` to process fewer commits
- Use `gpt-3.5-turbo` which has higher rate limits
- Add delays between requests (modify the code if needed)

### Memory Issues

For large repositories:

- Process commits in batches using `--max-commits`
- Use `--format json` and post-process the results
- Consider using `--max-tokens` to reduce token usage

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests (when available)
pytest tests/
```

### Code Structure

The codebase is organized into modules:

- **cli.py** - Handles argument parsing and main execution flow
- **config.py** - Configuration management and validation
- **git_utils.py** - Git repository operations (fetching commits, diffs)
- **ai_summarizer.py** - OpenAI API integration for generating summaries
- **formatters.py** - Output formatting (Markdown, JSON, CSV)
- **statistics.py** - Statistics calculation and reporting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Credits

LogChange uses:

- [GitPython](https://github.com/gitpython-developers/GitPython) for Git operations
- [OpenAI API](https://openai.com/) for AI-powered summaries
- [tqdm](https://github.com/tqdm/tqdm) for progress bars

## Support

For issues, questions, or contributions:

- 🐛 [Report bugs](https://github.com/matmulai/logchange/issues)
- 💡 [Request features](https://github.com/matmulai/logchange/issues)
- 📖 [Read the docs](https://github.com/matmulai/logchange)
