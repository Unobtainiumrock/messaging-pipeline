# Credential Tests

This directory contains tests to verify API credentials and service connections.

## Naming Conventions

- **File naming**: `test_<service>_credentials.py`
- **Function naming**: `test_<service>_credentials()`

## Example

```python
# test_example_credentials.py
def test_example_credentials():
    """Test Example API credentials."""
```

## Adding New Tests

1. Create a new file following the naming pattern
2. Implement the test function with the matching name
3. Your test will be automatically discovered by `pytest`

No additional configuration needed - the test runner finds all component tests based on filename.
