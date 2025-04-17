#!/usr/bin/env python3
"""
Script to add type annotations to a Python file using an LLM.

The script extracts functions and class definitions from the target file,
sends each block to the LLM for annotation, and rewrites the file with the updated types.
"""

import os
import sys
import ast
import logging
import re
from typing import List, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from tiktoken import Tokenizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "llm_type_annotations.log")
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables (for OPENAI_API_KEY)
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    logger.error("Error: OPENAI_API_KEY environment variable not set.")
    sys.exit(1)

# Create OpenAI client
client = OpenAI(api_key=API_KEY)


def extract_functions_and_classes(
    file_path: str,
) -> Tuple[List[Tuple[str, int, int]], List[Tuple[str, int, int]], str]:
    """
    Extract functions and classes from a Python file.

    Returns:
        functions: List of tuples (name, start_line, end_line) for each function.
        classes: List of tuples (name, start_line, end_line) for each class.
        source: The full file content.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    functions: List[Tuple[str, int, int]] = []
    classes: List[Tuple[str, int, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            end_line = getattr(node, "end_lineno", node.lineno)
            functions.append((node.name, node.lineno, end_line))
        elif isinstance(node, ast.ClassDef):
            end_line = getattr(node, "end_lineno", node.lineno)
            classes.append((node.name, node.lineno, end_line))

    return functions, classes, source


def call_llm_for_type_annotation(name: str, code_snippet: str) -> str:
    """Call the LLM to add type annotations to the given code snippet."""
    try:
        logger.info(f"Processing {name} for type annotations")

        prompt = f"""
Add Python type annotations to the following Python file.
Use typing module imports as needed (List, Dict, Optional, etc).
Be precise and follow PEP 484 guidelines.
Consolidate all import statements at the top of the file.
Do not change functionality or logic.
Only add or improve type annotations.

Here's the code to annotate:

{code_snippet}

Return only the fully annotated file without any explanations or markdown:
"""

        # Calculate tokens
        try:
            # Get exact token count for input
            encoder = Tokenizer(encoding_for_model="gpt-4")
            input_tokens = len(encoder.encode(code_snippet))

            # Also count the prompt template tokens
            prompt_template = """
Add Python type annotations to the following Python file.
Use typing module imports as needed (List, Dict, Optional, etc).
Be precise and follow PEP 484 guidelines.
Consolidate all import statements at the top of the file.
Do not change functionality or logic.
Only add or improve type annotations.

Here's the code to annotate:


Return only the fully annotated file without any explanations or markdown:
"""
            prompt_tokens = len(encoder.encode(prompt_template))

            # Determine model and max tokens
            total_input_tokens = input_tokens + prompt_tokens

            if total_input_tokens > 6000:
                model = "gpt-4-turbo"
                max_tokens = 128000 - total_input_tokens  # For GPT-4 Turbo (large context)
            else:
                model = "gpt-4"
                max_tokens = 8192 - total_input_tokens - 100  # Leave 100 token buffer
                max_tokens = max(1000, min(max_tokens, 7000))  # Reasonable bounds

        except Exception as e:
            # Fall back to estimation
            logger.warning(f"Token counting failed: {e}. Using estimation.")
            estimated_tokens = len(code_snippet.split()) * 2
            model = "gpt-4-turbo" if estimated_tokens > 3000 else "gpt-4"
            max_tokens = 6000 if model == "gpt-4" else 20000  # Conservative defaults

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=max_tokens,
        )

        annotated_code = response.choices[0].message.content.strip()

        # Clean up any markdown code block formatting
        annotated_code = re.sub(r"^```python\s*", "", annotated_code, flags=re.MULTILINE)
        annotated_code = re.sub(r"^```\s*$", "", annotated_code, flags=re.MULTILINE)

        logger.info(f"Successfully annotated {name}")
        return annotated_code

    except Exception as e:
        logger.error(f"Error annotating {name}: {str(e)}")
        return code_snippet  # Return original code if there's an error


def extract_code_segment(source: str, start_line: int, end_line: int) -> str:
    """Extract a segment of code from the source by line numbers."""
    lines = source.split("\n")
    # Adjust for zero-based indexing
    return "\n".join(lines[start_line - 1 : end_line])


def update_file_with_annotations(file_path: str, segments: List[Tuple[int, int, str]]) -> None:
    """
    Update the file with the annotated code segments.

    Args:
        file_path: Path to the file to update
        segments: List of tuples (start_line, end_line, annotated_code)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    # Sort segments by start_line in reverse order to avoid index shifts
    segments.sort(key=lambda x: x[0], reverse=True)

    for start_line, end_line, annotated_code in segments:
        # Convert to 0-based indexing
        start_idx = start_line - 1
        end_idx = end_line

        # Replace the segment with annotated code
        lines[start_idx:end_idx] = annotated_code.split("\n")

    # Write back to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"Updated file: {file_path}")


def process_file(file_path: str) -> None:
    """Process a single Python file for type annotations."""
    if not file_path.endswith(".py"):
        logger.warning(f"Skipping non-Python file: {file_path}")
        return

    logger.info(f"Processing file: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        # Make a single API call for the entire file
        annotated_code = call_llm_for_type_annotation(os.path.basename(file_path), source)

        # Write the annotated file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(annotated_code)

        logger.info(f"Updated file: {file_path}")

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")


def main() -> None:
    """Process Python files to add type annotations."""
    if len(sys.argv) < 2:
        logger.error("Usage: python type_annotate_python_files.py <file_or_directory_path>")
        sys.exit(1)

    target_path = sys.argv[1]

    if os.path.isfile(target_path):
        process_file(target_path)
    elif os.path.isdir(target_path):
        # Process all Python files in the directory
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    process_file(file_path)
    else:
        logger.error(f"Path not found: {target_path}")
        sys.exit(1)

    logger.info("Type annotation process completed")


if __name__ == "__main__":
    main()
