# Component Tests

This directory contains tests to verify service components.

## Naming Conventions

- **File naming**: `test_<service>.py`
- **Function naming**: `test_<service>()`

## Example

```python
# test_example_credentials.py
def test_example():
    """Test Example Component."""
```

## Adding New Tests

1. Create a new file following the naming pattern
2. Implement the test function with the matching name
3. Your test will be automatically discovered by `pytest`

No additional configuration needed - the test runner finds all component tests based on filename.
