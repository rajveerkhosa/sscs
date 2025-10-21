# Git Push Instructions

Follow these steps to push your SSCS Weekly Tracker project to GitHub.

## Prerequisites

- Git installed on your system
- GitHub account
- Repository created on GitHub (you'll need the URL)

## Step-by-Step Instructions

### 1. Initialize Git Repository (if not already done)

```bash
cd /Users/raj/SSCS
git init
```

### 2. Check What Will Be Committed

```bash
git status
```

**You should see:**
- ✅ Python files (.py)
- ✅ config.yaml
- ✅ .env.template
- ✅ requirements.txt
- ✅ README.md
- ✅ TROUBLESHOOTING.md
- ✅ Other documentation files

**You should NOT see:**
- ❌ .env (credentials)
- ❌ Weekly Tracker.xlsx (business data)
- ❌ backups/ folder
- ❌ logs/ folder
- ❌ __pycache__/

If you see files that should be ignored, double-check your .gitignore file.

### 3. Add All Files to Staging

```bash
git add .
```

### 4. Verify Files to Be Committed

```bash
git status
```

Review the list carefully. Make sure no sensitive files are included.

### 5. Create Initial Commit

```bash
git commit -m "Initial commit: SSCS Weekly Tracker automation

- Automated fuel gallons extraction from SSCS
- Excel tracker updates with rolling window
- Historical backfill capability
- Comprehensive logging and error handling
- Backup system for data protection"
```

### 6. Add Remote Repository

Replace `<your-github-username>` and `<repository-name>` with your actual values:

```bash
git remote add origin https://github.com/<your-github-username>/<repository-name>.git
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/sscs-tracker.git
```

### 7. Verify Remote Was Added

```bash
git remote -v
```

You should see:
```
origin  https://github.com/<your-username>/<repo-name>.git (fetch)
origin  https://github.com/<your-username>/<repo-name>.git (push)
```

### 8. Push to GitHub

```bash
git push -u origin main
```

**If you get an error about 'main' not existing**, try:
```bash
git branch -M main
git push -u origin main
```

### 9. Verify Push Was Successful

Go to your GitHub repository in a web browser:
```
https://github.com/<your-username>/<repository-name>
```

You should see all your files listed.

## Important Security Checks

Before pushing, verify these files are **NOT** in your repository:

```bash
# Check for .env file (should NOT be there)
git ls-files | grep "\.env$"

# Check for Excel file (should NOT be there)
git ls-files | grep "Weekly Tracker.xlsx"

# Check for backups (should NOT be there)
git ls-files | grep "backups/"

# Check for logs (should NOT be there)
git ls-files | grep "logs/"
```

All of the above commands should return **nothing**. If they show files, those files are tracked and you need to remove them:

```bash
# Remove a file from git (example)
git rm --cached .env
git commit -m "Remove sensitive file from git"
git push
```

## Future Updates

After making changes to your code:

```bash
# Check what changed
git status

# Add changed files
git add <filename>
# OR add all changes
git add .

# Commit with descriptive message
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## Troubleshooting

### "fatal: remote origin already exists"

```bash
# Remove existing remote
git remote remove origin

# Add it again with correct URL
git remote add origin https://github.com/<your-username>/<repo-name>.git
```

### "Permission denied (publickey)"

You need to set up SSH keys or use HTTPS with personal access token. For beginners, use HTTPS:

```bash
git remote set-url origin https://github.com/<your-username>/<repo-name>.git
```

When prompted, enter your GitHub username and personal access token (not password).

### "Updates were rejected"

Someone else pushed changes, or you're working from multiple locations:

```bash
git pull origin main
git push origin main
```

### Accidentally Committed Sensitive Files

If you committed `.env` or `Weekly Tracker.xlsx`:

```bash
# Remove from git but keep local copy
git rm --cached .env
git rm --cached "Weekly Tracker.xlsx"

# Commit the removal
git commit -m "Remove sensitive files"

# Push
git push
```

## Best Practices

1. **Never commit credentials** - Always use .env with .gitignore
2. **Never commit data files** - Excel files contain business data
3. **Write descriptive commit messages** - Explain what changed and why
4. **Commit often** - Small, logical commits are better than large ones
5. **Pull before pushing** - If working from multiple locations
6. **Review before committing** - Use `git status` and `git diff`

## Quick Reference

```bash
# Daily workflow
git status                    # Check what changed
git add .                     # Stage all changes
git commit -m "message"       # Commit changes
git push                      # Push to GitHub

# Check status
git status                    # Working directory status
git log                       # Commit history
git diff                      # See changes

# Undo changes
git checkout -- <file>        # Discard changes to file
git reset HEAD <file>         # Unstage file
git revert <commit>           # Undo a commit
```

## Done!

Your SSCS Weekly Tracker automation is now safely stored on GitHub! 🎉
