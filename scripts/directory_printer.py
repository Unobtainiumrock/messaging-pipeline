#!/usr/bin/env python3

import os
import sys

# List of directories/files to exclude from output
DEFAULT_IGNORED = {
    "node_modules", ".git", ".DS_Store", "__pycache__", "venv", ".idea",
    ".vscode", "dist", "build", "target", ".pytest_cache", "coverage",
    ".mypy_cache", "yarn.lock", "package-lock.json", "poetry.lock",
    ".next", ".turbo", "bin", "obj", "logs", ".gradle", ".svn", "env",
    ".tox", "__pypackages__", "output", ".history", "__snapshots__",
    "__tests__", "migrations", "__fixtures__", "venv", "virtualenv",
    
    # Python dependencies & package metadata
    "site-packages", "_vendor", ".dist-info", "pip", "setuptools",
    "pkg_resources", "wheel", "openai", "requests", "urllib3", "idna",
    "certifi", "msgpack", "platformdirs", "pygments", "rich", "distro",
    
    # Package manager metadata
    "INSTALLER", "METADATA", "RECORD", "WHEEL", "LICENSE", "py.typed",
    "entry_points.txt",
    
    # GIT repository internals (block `.git/` and all its subdirectories)
    ".git", ".git/hooks", ".git/info", ".git/logs", ".git/objects",
    ".git/refs", ".git/packed-refs", ".git/config", ".git/HEAD",
    ".git/description", ".git/index", ".git/branches", ".git/refs/tags",
    ".git/refs/remotes", ".git/refs/heads", ".git/refs/notes",
    
    # Miscellaneous redundant cache data
    "__pycache__", "cache", ".cache", "tmp", "tmp_files", "sessions",
}

def load_gitignore_patterns(startpath):
    """Loads patterns from .gitignore if present."""
    gitignore_path = os.path.join(startpath, ".gitignore")
    ignore_patterns = set(DEFAULT_IGNORED)

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.add(line.strip("/"))
    
    return ignore_patterns

def should_ignore(full_path, ignored_patterns):
    """Check if a full directory path should be ignored."""
    # Normalize path and check against ignored patterns
    relative_path = os.path.relpath(full_path, start=os.getcwd())
    
    return any(
        relative_path.startswith(pattern) or pattern in relative_path.split(os.sep)
        for pattern in ignored_patterns
    )

def print_dir_tree(startpath, ignore_clutter=False):
    """Prints a directory tree, filtering out unwanted files/directories."""
    
    ignored_patterns = load_gitignore_patterns(startpath) if ignore_clutter else set()

    print("comm-centralizer/")
    print("|")

    for root, dirs, files in os.walk(startpath, topdown=True):
        if root == startpath:
            continue  # Skip root directory, as it's printed separately
        
        # Skip directories that should be ignored
        if ignore_clutter and should_ignore(root, ignored_patterns):
            continue

        level = root.replace(startpath, '').count(os.sep)
        indent = '|   ' * level
        base_name = os.path.basename(root)

        print(f'{indent}|── {base_name}/')

        subindent = '|   ' * (level + 1)
        
        # Sort and filter directories & files
        dirs[:] = [d for d in sorted(dirs) if not (ignore_clutter and should_ignore(os.path.join(root, d), ignored_patterns))]
        files[:] = [f for f in sorted(files) if not (ignore_clutter and should_ignore(os.path.join(root, f), ignored_patterns))]
        
        # Process files within the current directory
        for i, f in enumerate(files):
            print(f"{subindent}|── {f}")

    # Print files in root directory
    files_in_root = sorted(
        [f for f in os.listdir(startpath) if os.path.isfile(os.path.join(startpath, f)) and not (ignore_clutter and should_ignore(os.path.join(startpath, f), ignored_patterns))]
    )

    for i, f in enumerate(files_in_root):
        print(f"{'└──' if i == len(files_in_root) - 1 else '|──'} {f}")

if __name__ == "__main__":
    startpath = "."
    ignore_clutter = False

    # Handle command-line arguments
    args = sys.argv[1:]
    if "-y" in args:
        ignore_clutter = True
        args.remove("-y")
    
    if args:
        startpath = args[0]

    print_dir_tree(startpath, ignore_clutter)
