# GITWiz Deployment Guide

GITWiz is an adaptive command node for the Aurora CloudBank repo. It performs
environment diagnostics, automatic fixes and assists with deployments to keep
the repository stable.

## Stage 1: Preparation
1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```
2. Ensure Python 3.11+ and Node 18+ are available.
3. Grant execution permission to the tool:
   ```bash
   chmod +x scripts/gitwiz.py
   ```

## Stage 2: Build
1. Run pre-checks to verify repository health:
   ```bash
   python scripts/gitwiz.py precheck
   ```
   - Runs `git status`, Python linting, JavaScript linting and unit tests.
2. Apply automatic fixes when needed:
   ```bash
   python scripts/gitwiz.py fix
   ```
   - Executes `black`, `isort` and `eslint --fix`.
3. Re-run `python scripts/gitwiz.py precheck` to confirm a clean state.

## Stage 3: Deploy
1. Deploy changes through the wizard:
   ```bash
   python scripts/gitwiz.py deploy
   ```
   - Stages all files and creates a commit using a standard message.
2. Push to the main branch after reviewing the commit:
   ```bash
   git push origin main
   ```
3. Optionally set up a pre-commit hook to run `gitwiz.py precheck` automatically:
   ```bash
   ln -s ../../scripts/gitwiz.py .git/hooks/pre-commit
   ```

GITWiz keeps the repo stable by combining lint checks, unit tests and automation.
Customize the script to expand its heuristics or integrate additional actions as
the project evolves.

## Branch and PR Management
GITWiz also streamlines branch operations and pull request creation.

### Branch commands
```bash
python scripts/gitwiz.py branch list
python scripts/gitwiz.py branch create feature-xyz --base main
python scripts/gitwiz.py branch checkout feature-xyz
python scripts/gitwiz.py branch merge feature-xyz main
python scripts/gitwiz.py branch delete feature-xyz
```

### Create a pull request
```bash
python scripts/gitwiz.py pr --title "My feature" --body "Adds awesome stuff"
```
This command requires the GitHub CLI (`gh`) to be installed. Otherwise, push
your branch and open a PR manually.
