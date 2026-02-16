# GitHub Actions Setup Guide

This guide will walk you through setting up and using GitHub Actions for this project.

## Prerequisites

1. A GitHub account
2. This repository pushed to GitHub (either as a new repository or an existing one)

## Step 1: Push Your Code to GitHub

If you haven't already, create a new repository on GitHub and push your code:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Observer pattern trading system"

# Add your GitHub repository as remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

## Step 2: Verify GitHub Actions Workflow

The GitHub Actions workflow file is already created at `.github/workflows/ci.yml`. It will automatically:

- Run on every push to `main`, `master`, or `develop` branches
- Run on every pull request to those branches
- Install Python 3.11
- Install dependencies from `requirements.txt`
- Run the test suite with pytest
- Generate a coverage report
- **Fail the build if coverage is below 90%**

## Step 3: Check Workflow Status

1. Go to your GitHub repository
2. Click on the **"Actions"** tab at the top
3. You should see your workflow runs listed there
4. Click on a run to see detailed logs

## Step 4: Understanding the Workflow

The CI pipeline does the following:

```yaml
1. Checkout code
2. Set up Python 3.11
3. Cache pip packages (for faster builds)
4. Install dependencies from requirements.txt
5. Run tests with coverage: `coverage run -m pytest -q`
6. Generate coverage report: `coverage report --fail-under=90`
```

## Step 5: Viewing Coverage Reports

The coverage report will show:
- Which files are covered
- Line-by-line coverage percentages
- Missing lines (if any)

If coverage is below 90%, the build will fail with an error message.

## Step 6: Making Changes and Testing Locally

Before pushing, you can test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
coverage run -m pytest
coverage report

# Generate HTML coverage report (optional)
coverage html
# Then open htmlcov/index.html in your browser
```

## Step 7: Troubleshooting

### Build Fails Due to Low Coverage

If your build fails because coverage is below 90%:

1. Check the coverage report in the Actions tab
2. Identify which files/lines are not covered
3. Add tests for the missing coverage
4. Run `coverage report` locally to verify before pushing

### Tests Fail

1. Check the error messages in the Actions tab
2. Run tests locally: `pytest -v`
3. Fix the failing tests
4. Push again

### Python Version Issues

The workflow uses Python 3.11. If you need a different version, edit `.github/workflows/ci.yml`:

```yaml
python-version: "3.11"  # Change to your desired version
```

## Step 8: Adding a Coverage Badge (Optional)

You can add a coverage badge to your README. Add this line to your README.md:

```markdown
![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)
```

Or use a service like Codecov (already configured in the workflow) for automatic badges.

## Workflow File Location

The workflow file is located at:
```
.github/workflows/ci.yml
```

You can edit this file to:
- Change Python version
- Add more test steps
- Add linting steps
- Add deployment steps
- Change trigger conditions

## Example Workflow Run

When you push code, you'll see:

1. A yellow dot (⏳) next to your commit - workflow is running
2. A green checkmark (✅) - all tests passed and coverage ≥90%
3. A red X (❌) - tests failed or coverage <90%

Click on the status icon to see detailed logs.

## Next Steps

1. Push your code to GitHub
2. Check the Actions tab to see your first workflow run
3. Verify all tests pass and coverage is ≥90%
4. Make changes and watch the CI run automatically!

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

