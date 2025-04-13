# Repository Guidelines

## Large Files and Backups

This repository is set up to prevent the accidental commit of large files and backup archives. The following measures are in place:

### 1. .gitignore Configuration

Multiple patterns in `.gitignore` ensure that backups and large binary files are never tracked:

```
# Project specific - NEVER commit these directories
backups/
/backups
/backups/
backups/*
/models/ltx-video/
models/ltx-video
/models/ltx-video
*/backups/
```

### 2. Local .git/info/exclude

Additional exclusion patterns are defined in the local `.git/info/exclude` file for extra protection.

### 3. Pre-commit Hook

A pre-commit hook checks for:
- Files in the `backups/` directory
- Any files larger than 10MB

If detected, the commit will be blocked with an error message.

## Managing Large Files

For large files such as backups, models, and media assets, consider:

1. Storing them on a separate secure server or cloud storage
2. Using Git LFS (Large File Storage) if they must be version-controlled
3. Implementing a separate backup solution for critical data

## Backup Strategy

Backups should be:
- Stored locally in the `backups/` directory (which is excluded from Git)
- Regularly copied to a secure external location
- Documented with clear naming conventions and timestamps

## Before Pushing to GitHub

Always verify that you're not pushing large files by using:

```bash
git status
git diff --cached --name-only
```

If you accidentally stage a large file, you can unstage it with:

```bash
git reset HEAD path/to/large/file
```