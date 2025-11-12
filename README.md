## LogChange: GenAI Assisted Changelog & Commit Message Generation

LogChange provides AI-powered tools for generating both project changelogs and commit messages using OpenAI. The suite includes:

- **Changelog Generator**: Summarizes git commits into human-readable changelogs
- **Commit Message Generator**: Creates high-quality commit messages from diffs
- **Smart Caching**: Reduces API costs by caching responses
- **Rate Limiting**: Prevents API quota exhaustion

### Requirements

- Python 3.8+
- An OpenAI API key (`OPENAI_API_KEY` environment variable)

Install dependencies with:

```bash
pip install -r requirements.txt
```

### Usage

#### Generating Changelogs

Run the changelog generator from the repository root:

```bash
export OPENAI_API_KEY=sk-your-key
python scripts/gen_changelog.py --max-commits 100 --output CHANGELOG.md
```

#### Generating Commit Messages

Generate a commit message for staged changes:

```bash
export OPENAI_API_KEY=sk-your-key
python scripts/gen_commit_msg.py --staged --style conventional
```

Generate a message for a specific commit:

```bash
python scripts/gen_commit_msg.py --commit abc1234 --style detailed
```

Available styles:
- `conventional`: Follows Conventional Commits format (feat:, fix:, etc.)
- `concise`: Single-line, brief messages
- `detailed`: Multi-line with extensive explanation

Options:
- `--staged`: Generate message for staged changes
- `--commit HASH`: Generate message for specific commit
- `--style STYLE`: Message style (conventional, concise, detailed)
- `--model MODEL`: OpenAI model to use (default: gpt-4)
- `--no-cache`: Disable response caching
- `--clear-cache`: Clear all cached responses

Use `--help` on any script to see all available options.

