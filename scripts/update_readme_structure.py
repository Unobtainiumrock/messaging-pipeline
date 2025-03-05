#!/usr/bin/env python3
"""
Script to update the README.md with the current project structure with explanatory comments.
This script can be used as a pre-commit hook.
"""
import os
import re
import subprocess
import json
from dotenv import load_dotenv
import io
import sys
from pathlib import Path
from openai import OpenAI  # Import the OpenAI client

# Import the directory printer functionality
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from directory_printer import print_dir_tree

# Load environment variables for API keys
load_dotenv()

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
        
        print(response)

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
    print("="*100)
    print(directory_structure)
    print("="*100)
    
    print("Adding explanatory comments with LLM...")
    annotated_structure = add_comments_with_llm(directory_structure)
    
    print("Updating README.md...")
    update_readme(annotated_structure)

if __name__ == "__main__":
    main() 

