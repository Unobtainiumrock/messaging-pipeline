<think>
Let me walk through the pre-commit workflow with Docker integration from start to finish to give a clear picture of how the scripts fit into the pipeline.

The key components:

1. `.pre-commit-config.yaml` - Defines the pre-commit hooks
2. `scripts/docker-pre-commit.sh` - Script to run pre-commit in Docker
3. `.git/hooks/pre-commit` - Git hook that triggers on commit
4. Docker and docker-compose - Manages the isolated environment

The data flow/process:
</think>

# Complete Pre-commit Pipeline with Docker Integration

Let me explain the entire data flow of your pre-commit pipeline with Docker integration, from the moment you run `git commit` to when all checks complete.

## Pipeline Overview

```
┌─────────────────┐     ┌──────────────────────┐     ┌───────────────────────┐
│                 │     │                      │     │                       │
│  git commit     │────▶│  Git Hook System     │────▶│  docker-pre-commit.sh │
│                 │     │  (.git/hooks)        │     │                       │
└─────────────────┘     └──────────────────────┘     └───────────┬───────────┘
                                                                 │
                                                                 ▼
┌─────────────────┐     ┌──────────────────────┐     ┌───────────────────────┐
│                 │     │                      │     │                       │
│  Commit Success │◀────│  Pre-commit Hooks    │◀────│  Docker Container     │
│  or Failure     │     │  (.pre-commit-config)│     │  (Python 3.11)        │
└─────────────────┘     └──────────────────────┘     └───────────────────────┘
```

## Step-by-Step Data Flow

### 1. Developer Initiates a Commit

```bash
git add file.py
git commit -m "Update code"
```

### 2. Git's Built-in Hook System Activates

- Git checks for hooks in `.git/hooks/`
- Finds and executes our custom pre-commit hook

### 3. Our Custom Git Hook (`.git/hooks/pre-commit`)

- Determines which files are staged for commit
- Passes this list to our Docker pre-commit script
- Script contents:
  ```bash
  #!/bin/bash
  STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)
  ./scripts/docker-pre-commit.sh $STAGED_FILES
  ```

### 4. Docker Pre-commit Script (`scripts/docker-pre-commit.sh`)

- Takes the list of staged files
- Launches a Docker container using your development environment
- Runs pre-commit within that container
- Script contents:
  ```bash
  #!/bin/bash
  docker-compose -f docker-compose.dev.yml run --rm app pre-commit run --files "$@"
  ```

### 5. Docker Container Executes

- Container starts with Python 3.11
- All system dependencies installed
- Project code mounted from your local system
- Isolates the execution environment completely

### 6. Pre-commit Framework Runs Inside Container

- Reads `.pre-commit-config.yaml`
- Executes each configured hook:
  - `update-readme-structure`
  - `pytype-annotations` (uses Python 3.12 from your config)
  - `typescript-strict-check`
  - `black`, `flake8`, `prettier`, `eslint`, etc.

### 7. Results Flow Back Through the Pipeline

- Pre-commit exits with success (0) or failure (non-zero)
- Docker container exits with the same code
- `docker-pre-commit.sh` exits with the same code
- Git hook succeeds or fails based on this exit code
- Git either proceeds with the commit or aborts

## Why Separate Shell Scripts?

1. **Separation of Concerns**:

   - Git hook handles staging detection
   - Docker script handles environment setup

2. **Maintainability**:

   - Easier to update Docker configuration separately
   - Prevents complex logic inside Git hook

3. **Reusability**:

   - Docker script can be used by CI/CD or manually
   - Can be called with different file sets

4. **Portability**:
   - Works across different developer machines
   - Standardizes the development environment

## Benefits of This Approach

1. **Version Consistency**: Everyone uses the same Python version (3.11 in Docker)
2. **System Isolation**: Dependencies don't conflict with your local system
3. **Reproducibility**: CI/CD can use the same Docker image
4. **Flexibility**: Your local system can use any Python version (3.12)

This approach lets you standardize on Python 3.11 for the project while your system can continue to use Python 3.12 or any version you prefer.
