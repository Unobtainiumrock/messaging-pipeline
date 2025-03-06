#!/usr/bin/env python3
"""
Script to update the README.md with the current project structure with explanatory comments.
This script can be used as a pre-commit hook.
"""
import os
import re
import subprocess
import json
import io
import sys
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI  # Import the OpenAI client

# Import the directory printer functionality
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from directory_printer import print_dir_tree

# Load environment variables for API keys
load_dotenv()

# Cache file for storing the last directory structure hash
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".dir_structure_cache.json")

def get_directory_structure():
    """Get the directory structure using the imported print_dir_tree function."""
    # Capture the output of print_dir_tree
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    # Call the print_dir_tree function with ignore_clutter=True
    print_dir_tree(os.getcwd(), ignore_clutter=True)
    
    # Get the output and restore stdout
    output = new_stdout.getvalue()
    sys.stdout = old_stdout
    
    return output

def calculate_structure_hash(structure):
    """Calculate a hash of the directory structure to detect changes."""
    return hashlib.md5(structure.encode('utf-8')).hexdigest()

def is_structure_changed(structure):
    """Check if the directory structure has changed since last update."""
    structure_hash = calculate_structure_hash(structure)
    
    # If cache file exists, read the previous hash
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
            previous_hash = cache.get('structure_hash')
            return structure_hash != previous_hash
        except (json.JSONDecodeError, KeyError):
            # If cache file is corrupted, assume structure has changed
            return True
    
    # If no cache file, assume structure has changed
    return True

def update_cache(structure):
    """Update the cache file with the current structure hash."""
    structure_hash = calculate_structure_hash(structure)
    cache = {'structure_hash': structure_hash}
    
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def add_comments_with_llm(directory_structure):
    """Send the directory structure to an LLM to add explanatory comments using OpenAI SDK."""
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return directory_structure

    # Create OpenAI client
    client = OpenAI(api_key=api_key)

    # Prepare the prompt
    prompt = f"""
I have a project directory structure and I need you to add explanatory comments for each file and directory.
You should use the same format as the example below with each comment aligned and using # to start comments.

Here's the format example:
```
comm-centralizer/
├── .env.example               # Template for environment variables
├── .gitignore                 # Git ignore file
├── README.md                  # Project documentation
├── src/                       # Source code
│   ├── connectors/            # API connections to various platforms
│   │   ├── email_connector.py     # Gmail/Outlook API integration
```

Keep your comments brief but informative. Don't add comments to __init__.py files.
Add more detailed comments for important files like connectors, processors, etc.

Here's my project structure:
{directory_structure}

Please format it with the same style as the example, with proper indentation and comments.
Only return the formatted directory structure, nothing else.
"""

    # Call OpenAI API using the SDK
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract content from response
        content = response.choices[0].message.content
        
        # Extract the code block if present
        code_block_match = re.search(r"```(?:bash)?\n([\s\S]+?)\n```", content)
        if code_block_match:
            return code_block_match.group(1)
        return content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return directory_structure

def update_readme(annotated_structure):
    """Update the README.md file with the new annotated structure."""
    # Get the project root directory (parent of scripts directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from scripts/
    readme_path = os.path.join(project_root, "README.md")
    
    if not os.path.exists(readme_path):
        print(f"Error: README.md not found at {readme_path}")
        return False
    
    with open(readme_path, 'r') as file:
        content = file.read()
    
    # Look for the Project Structure section and code block
    pattern = r"## Project Structure\s*\n\s*```[^\n]*\n([\s\S]*?)\n```"
    match = re.search(pattern, content)
    
    if match:
        # Replace the existing structure with the new one
        new_content = re.sub(
            pattern,
            f"## Project Structure\n\n```bash\n{annotated_structure}\n```",
            content
        )
        
        with open(readme_path, 'w') as file:
            file.write(new_content)
        
        print(f"README.md successfully updated at {readme_path}")
        return True
    else:
        print(f"Error: Could not find Project Structure section in README.md at {readme_path}")
        return False

def main():
    """Main function to update README with annotated directory structure."""
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    print(f"Using project root: {project_root}")
    print("Fetching directory structure...")
    directory_structure = get_directory_structure()
    
    # Check if structure has changed
    if not is_structure_changed(directory_structure):
        print("Project structure unchanged. Skipping update.")
        return
    
    print("Project structure has changed. Proceeding with update...")
    
    print("Adding explanatory comments with LLM...")
    annotated_structure = add_comments_with_llm(directory_structure)
    
    print("Updating README.md...")
    success = update_readme(annotated_structure)
    
    if success:
        # Update the cache with the new structure
        update_cache(directory_structure)
        print("Cache updated with new directory structure.")

if __name__ == "__main__":
    main() 

