# Credential Tests

This directory contains tests to verify API credentials and service connections.

## Naming Conventions

- **File naming**: `test_<service>_credentials.py`
- **Function naming**: `test_<service>_credentials()`
- **Return value**: `True` if credentials are valid, `False` otherwise

## Example

```python
# test_example_credentials.py
def test_example_credentials():
    """Test Example API credentials."""
    # Verify credentials...
    if successful:
        return True
    else:
        return False
```

## Adding New Tests

1. Create a new file following the naming pattern
2. Implement the test function with the matching name
3. Your test will be automatically discovered by `run_credential_tests.py`

No additional configuration needed - the test runner finds all credential tests based on filename. 