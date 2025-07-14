## LogChange: GenAI Assisted Changelog Generation

LogChange generates a project changelog by summarizing git commits with OpenAI.
The provided GitHub Action runs the script automatically on new commits, but it
can also be executed locally.

### Requirements

- Python 3.8+
- An OpenAI API key (`OPENAI_API_KEY` environment variable)

Install dependencies with:

```bash
pip install -r requirements.txt
```

### Usage

Run the script from the repository root:

```bash
export OPENAI_API_KEY=sk-your-key
python scripts/gen_changelog.py --max-commits 100 --output CHANGELOG.md
```

Use `--help` to see all available options.

