# Git Commands for Cloud Engineers

## Essential Git Commands for MLOps Platform

### Initial Setup

```bash
# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Clone repository
git clone https://github.com/your-org/mlops-platform.git
cd mlops-platform
```

### Branch Management

```bash
# Create feature branch
git checkout -b feature/medication-adherence-model

# List branches
git branch -a

# Switch branch
git checkout main

# Delete branch
git branch -d feature/medication-adherence-model

# Rename branch
git branch -m old-name new-name
```

### Committing Changes

```bash
# Check status
git status

# Stage all changes
git add .

# Stage specific file
git add src/pipelines/training_pipeline.py

# Commit changes
git commit -m "Add medication adherence training pipeline"

# Amend last commit
git commit --amend --no-edit

# View commit history
git log --oneline -10
```

### Pushing and Pulling

```bash
# Push to remote
git push origin feature/medication-adherence-model

# Pull latest changes
git pull origin main

# Fetch without merging
git fetch origin

# Push all branches
git push origin --all
```

### Merging and Rebasing

```bash
# Merge branch into main
git checkout main
git merge feature/medication-adherence-model

# Rebase branch
git rebase main

# Interactive rebase
git rebase -i HEAD~3

# Abort rebase
git rebase --abort
```

### Stashing Changes

```bash
# Stash uncommitted changes
git stash

# List stashes
git stash list

# Apply stash
git stash apply stash@{0}

# Drop stash
git stash drop stash@{0}
```

### Undoing Changes

```bash
# Discard changes in working directory
git checkout -- src/pipelines/training_pipeline.py

# Unstage file
git reset HEAD src/pipelines/training_pipeline.py

# Revert commit
git revert abc1234

# Reset to previous commit
git reset --hard HEAD~1
```

### Viewing Changes

```bash
# Show diff
git diff

# Show staged diff
git diff --staged

# Show commit details
git show abc1234

# Show file history
git log -p src/pipelines/training_pipeline.py
```

### Remote Management

```bash
# List remotes
git remote -v

# Add remote
git remote add upstream https://github.com/upstream/repo.git

# Remove remote
git remote remove upstream

# Change remote URL
git remote set-url origin https://github.com/new-org/repo.git
```

### Tags

```bash
# Create tag
git tag v1.0.0

# Push tag
git push origin v1.0.0

# List tags
git tag -l

# Delete tag
git tag -d v1.0.0
```

### Collaboration

```bash
# Create pull request (GitHub CLI)
gh pr create --title "Add medication adherence model" --body "Implements RandomForest model"

# View pull requests
gh pr list

# Merge pull request
gh pr merge 123

# Check out pull request
gh pr checkout 123
```

### Debugging

```bash
# Find commit that introduced bug
git bisect start
git bisect bad HEAD
git bisect good v1.0.0

# Search commit history
git log -S "medication_adherence" --oneline

# Show who changed each line
git blame src/pipelines/training_pipeline.py

# Find lost commits
git reflog
```

## Branching Strategies

### Git Flow Strategy (Recommended for MLOps Platform)

```
main (production)
  ├── release/v1.0.0
  └── hotfix/critical-bug

develop (staging)
  ├── feature/medication-adherence-model
  ├── feature/drift-detection
  ├── feature/dashboard-ui
  └── bugfix/training-timeout
```

#### Branch Types

**main**: Production-ready code
- Only merged from release or hotfix branches
- Tagged with version numbers
- Protected branch (requires PR review)

**develop**: Integration branch
- Base for feature branches
- Deployed to staging environment
- Protected branch (requires PR review)

**feature/**: New features
- Branch from: `develop`
- Merge back to: `develop`
- Naming: `feature/medication-adherence-model`

**bugfix/**: Bug fixes
- Branch from: `develop`
- Merge back to: `develop`
- Naming: `bugfix/training-timeout`

**release/**: Release preparation
- Branch from: `develop`
- Merge to: `main` and `develop`
- Naming: `release/v1.0.0`

**hotfix/**: Production fixes
- Branch from: `main`
- Merge to: `main` and `develop`
- Naming: `hotfix/critical-bug`

#### Git Flow Commands

```bash
# Initialize Git Flow
git flow init

# Start feature
git flow feature start medication-adherence-model

# Finish feature (merges to develop)
git flow feature finish medication-adherence-model

# Start release
git flow release start 1.0.0

# Finish release (merges to main and develop)
git flow release finish 1.0.0

# Start hotfix
git flow hotfix start critical-bug

# Finish hotfix (merges to main and develop)
git flow hotfix