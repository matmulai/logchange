# LogChange Quality Assessment Guide

This guide helps you test and evaluate the AI-powered commit message generator.

## Quick Start

### 1. Setup

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# Or use a cheaper model for testing
export OPENAI_MODEL=gpt-3.5-turbo
```

### 2. Test the Tool on Recent Commits

We've made 6 real commits to improve this tool. Test the AI generator on each one:

```bash
# Get list of recent commits
git log --oneline -6

# For each commit hash, generate AI messages
python scripts/gen_commit_msg.py --commit <HASH> --style conventional
python scripts/gen_commit_msg.py --commit <HASH> --style concise
python scripts/gen_commit_msg.py --commit <HASH> --style detailed
```

### 3. Run the Automated Quality Demo

This will generate AI messages for all 6 commits and create a comparison report:

```bash
python scripts/demo_commit_quality.py
```

This creates `COMMIT_QUALITY_REPORT.md` with side-by-side comparisons.

## Manual Testing Methods

### Method 1: Test on Staged Changes

Make a change to any file, then:

```bash
git add .
python scripts/gen_commit_msg.py --staged --style conventional
```

Compare the AI suggestion with what you would write.

### Method 2: Test on Specific Past Commits

Pick interesting commits from your history:

```bash
# Find commits
git log --oneline --all | head -20

# Test the generator
python scripts/gen_commit_msg.py --commit abc1234 --style conventional
```

### Method 3: Batch Testing

Test all three styles on the same commit:

```bash
COMMIT_HASH="abc1234"

echo "=== CONVENTIONAL ==="
python scripts/gen_commit_msg.py --commit $COMMIT_HASH --style conventional

echo -e "\n=== CONCISE ==="
python scripts/gen_commit_msg.py --commit $COMMIT_HASH --style concise

echo -e "\n=== DETAILED ==="
python scripts/gen_commit_msg.py --commit $COMMIT_HASH --style detailed
```

## Quality Assessment Criteria

When evaluating the AI-generated messages, consider:

### 1. **Accuracy**
- Does the message correctly describe what changed?
- Are technical details accurate?
- Does it capture the "why" not just the "what"?

### 2. **Clarity**
- Is the message easy to understand?
- Would someone unfamiliar with the code understand it?
- Is the language concise but complete?

### 3. **Style Consistency**
- Does "conventional" follow Conventional Commits format?
- Are type prefixes (feat:, fix:, refactor:) used correctly?
- Is the imperative mood maintained?

### 4. **Completeness**
- Are breaking changes mentioned?
- Are important technical details included?
- Is the scope/context clear?

### 5. **Usefulness**
- Would this message be helpful in a changelog?
- Does it provide value beyond reading the diff?
- Could you understand the change from the message alone?

## Example Evaluation Template

For each commit, rate 1-5 stars:

```
Commit: abc1234
Actual Message: "Update README with new features"

AI Generated (Conventional):
"docs: enhance README with commit message generator documentation

Add comprehensive usage examples and feature descriptions for the new
commit message generator. Include examples for all three style options
and caching configuration."

Ratings:
├─ Accuracy:      ⭐⭐⭐⭐⭐ (5/5) - Perfectly describes changes
├─ Clarity:       ⭐⭐⭐⭐⭐ (5/5) - Very clear and detailed
├─ Style:         ⭐⭐⭐⭐⭐ (5/5) - Perfect Conventional Commits format
├─ Completeness:  ⭐⭐⭐⭐⭐ (5/5) - Captures all key changes
└─ Usefulness:    ⭐⭐⭐⭐⭐ (5/5) - Much more informative than original

Overall: 5/5 ⭐⭐⭐⭐⭐

Notes:
- AI message is more detailed and follows best practices
- Captures the "what" and "why" effectively
- Original message is generic; AI adds valuable context
```

## Testing Different Scenarios

### Small Changes
```bash
# Make a tiny change (fix typo, etc)
echo "# Test" >> test.txt
git add test.txt
python scripts/gen_commit_msg.py --staged
```

**Expected:** Concise, appropriate for small changes

### Large Refactors
```bash
# Test on a commit that refactored multiple files
python scripts/gen_commit_msg.py --commit <refactor-hash> --style detailed
```

**Expected:** Comprehensive explanation of structural changes

### Bug Fixes
```bash
# Test on a bug fix commit
python scripts/gen_commit_msg.py --commit <bugfix-hash> --style conventional
```

**Expected:** "fix:" prefix, clear description of issue resolved

### New Features
```bash
# Test on a feature addition
python scripts/gen_commit_msg.py --commit <feature-hash> --style conventional
```

**Expected:** "feat:" prefix, benefit-focused description

## Cost Analysis

Track API costs during testing:

```bash
# Each API call costs approximately:
# - GPT-4: ~$0.03 - $0.10 per message
# - GPT-3.5-turbo: ~$0.002 per message

# The caching feature reduces costs:
# - First run: Full API cost
# - Subsequent runs: Free (from cache)

# Test caching:
python scripts/gen_commit_msg.py --commit abc1234  # Costs money
python scripts/gen_commit_msg.py --commit abc1234  # Free (cached)

# Clear cache:
python scripts/gen_commit_msg.py --clear-cache
```

## Integration Testing

### Use in Real Workflow

Try using the tool for your next commit:

```bash
# 1. Make changes
vim some_file.py

# 2. Stage changes
git add some_file.py

# 3. Generate message
python scripts/gen_commit_msg.py --staged --style conventional > .git/COMMIT_MSG

# 4. Review and edit if needed
cat .git/COMMIT_MSG

# 5. Use it
git commit -F .git/COMMIT_MSG
```

### Create a Git Alias

```bash
# Add to ~/.gitconfig:
[alias]
    ai-commit = "!f() { \
        python scripts/gen_commit_msg.py --staged --style conventional; \
    }; f"

# Then use:
git add .
git ai-commit
```

## Comparison Report

After running `python scripts/demo_commit_quality.py`, you'll get a markdown report with:

- ✅ All actual commit messages
- ✅ AI-generated alternatives (3 styles each)
- ✅ Side-by-side comparison
- ✅ Space for your ratings and notes

Review `COMMIT_QUALITY_REPORT.md` to assess quality systematically.

## Success Metrics

The tool is working well if:

1. ✅ AI messages are as good or better than actual messages 70%+ of the time
2. ✅ "Conventional" style follows format correctly 95%+ of the time
3. ✅ Messages capture key technical details from the diff
4. ✅ Messages are more descriptive than typical human-written ones
5. ✅ Caching works and reduces repeat costs to $0
6. ✅ Error handling gracefully manages API issues

## Troubleshooting

### No API Key
```
Error: OpenAI API key is not set
→ Solution: export OPENAI_API_KEY=sk-your-key
```

### Rate Limit Errors
```
Error: OpenAI rate limit exceeded
→ Solution: Wait a minute, or reduce test frequency
→ The built-in rate limiter should prevent this
```

### Cache Issues
```bash
# Clear cache if you get stale results
python scripts/gen_commit_msg.py --clear-cache
```

### Import Errors
```bash
# Make sure you're in the repo root
cd /path/to/logchange

# Check dependencies
pip install -r requirements.txt
```

## Next Steps

After assessment:

1. 📊 Review `COMMIT_QUALITY_REPORT.md`
2. 📝 Note patterns: where AI excels vs. struggles
3. 🎯 Consider adjusting prompts in `gen_commit_msg.py` if needed
4. 🚀 Integrate into your workflow if quality is good
5. 💡 Share feedback on what works and what doesn't

## Real Commits to Test

Here are the 6 commits we made during this session:

1. `3d5115a` - Updated OpenAI API (deprecation fix)
2. `6cccc5e` - Added new commit message generator
3. `fc62444` - Added caching utilities
4. `90e5aed` - Integrated caching and error handling
5. `5d3f749` - Updated README
6. `80003f3` - Added demo script

Each represents a different type of change - perfect for quality testing!

```bash
# Quick test all 6:
for commit in 3d5115a 6cccc5e fc62444 90e5aed 5d3f749 80003f3; do
    echo "=== Testing $commit ==="
    python scripts/gen_commit_msg.py --commit $commit --style conventional
    echo ""
done
```
