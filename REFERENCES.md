# References for Python Type Annotation Tools

## LLM Model Specifications and Limitations

### Token Limits by Model

| Model         | Maximum Tokens | Recommended for                   |
| ------------- | -------------- | --------------------------------- |
| GPT-4 Turbo   | 128,000 tokens | Large files (up to ~40,000 words) |
| GPT-4         | 8,192 tokens   | Medium files (up to ~2,500 words) |
| GPT-3.5 Turbo | 16,384 tokens  | Medium files (up to ~5,000 words) |

### Token Estimation

- 1 token ≈ 0.75 words in English text
- Python code: ~1.5 tokens per word/symbol
- A typical 300-line Python file consumes ~3,000-4,000 tokens

## Alternative Implementation: Chunking Based on Token Limits

For processing very large files that might exceed token limits, implement a chunking strategy:

```python
def process_file_with_chunking(file_path: str, chunk_size: int = 5) -> None:
    """Process a file by chunking functions together for fewer API calls."""

    functions, classes, source = extract_functions_and_classes(file_path)

    # Combine functions and classes
    all_elements = functions + classes
    all_elements.sort(key=lambda x: x[1])  # Sort by start line

    # Create chunks
    chunks = [all_elements[i:i+chunk_size] for i in range(0, len(all_elements), chunk_size)]

    # Process each chunk
    annotated_segments = []
    for chunk in chunks:
        # Extract code for all elements in the chunk
        combined_code = ""
        for name, start_line, end_line in chunk:
            segment = extract_code_segment(source, start_line, end_line)
            combined_code += f"\n\n# Function/Class: {name}\n{segment}"

        # Annotate the combined chunk
        annotated_chunk = call_llm_for_type_annotation("Batch", combined_code)

        # Split the annotated code back into segments
        # This requires implementing a parser to identify function boundaries
        split_segments = split_annotated_code(annotated_chunk, chunk)

        for (name, start_line, end_line), segment in zip(chunk, split_segments):
            annotated_segments.append((start_line, end_line, segment))

    # Update file with all annotated segments
    update_file_with_annotations(file_path, annotated_segments)


def split_annotated_code(annotated_code: str, chunk: List[Tuple[str, int, int]]) -> List[str]:
    """Split annotated code back into segments based on function/class names."""
    segments = []
    lines = annotated_code.split('\n')
    current_segment = []
    current_idx = 0

    for line in lines:
        if line.startswith(f"# Function/Class: {chunk[current_idx][0]}"):
            if current_segment:
                segments.append('\n'.join(current_segment))
                current_segment = []
                current_idx += 1
                if current_idx >= len(chunk):
                    break
        else:
            current_segment.append(line)

    if current_segment:
        segments.append('\n'.join(current_segment))

    return segments
```

## Advanced Thresholding Logic

For optimal file processing, implement thresholding logic:

```python
def determine_processing_strategy(file_path: str) -> str:
    """Determine the best processing strategy based on file size."""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    # Estimate tokens
    estimated_tokens = len(source.split()) * 1.5

    if estimated_tokens < 6000:
        return "whole_file"
    elif estimated_tokens < 100000:
        return "gpt4_turbo"
    else:
        return "chunking"

def process_file_with_strategy(file_path: str) -> None:
    """Process a file using the optimal strategy."""
    strategy = determine_processing_strategy(file_path)

    if strategy == "whole_file":
        # Process entire file with GPT-4
        process_whole_file(file_path, model="gpt-4")
    elif strategy == "gpt4_turbo":
        # Process entire file with GPT-4 Turbo
        process_whole_file(file_path, model="gpt-4-turbo")
    else:
        # Use chunking strategy for very large files
        process_file_with_chunking(file_path)
```

## Performance Benchmarks

Based on published data and testing:

- GPT-4 achieves ~90% accuracy on Python type annotation tasks
- Processing time scales approximately linearly with file size
- Whole-file processing produces more consistent imports and type declarations
- Chunking produces less consistent results but works for very large files
- For files >50,000 tokens, chunking is the only viable option

## Cost Considerations

- Whole-file processing: Most efficient for cost/token
- Chunking with large chunks (5-10 functions): Good balance of cost vs. consistency
- Function-by-function: Highest cost, most redundant imports

## Future Improvements

- Implement AST-based parsing to better split chunked results
- Add support for preserving docstring formatting
- Add a dry-run option to preview changes without writing to files
- Consider implementing a cache for previously processed functions
