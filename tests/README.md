# Test Organization

This directory contains all test files for the MCP project. Tests are organized by feature area and type.

## Test Structure

```
tests/
├── api/                 # API-related tests
│   ├── middleware/      # Middleware tests
│   │   ├── test_security_middleware.py    # Security middleware tests
│   │   └── test_rate_limiting.py         # Rate limiting tests
│   ├── routers/        # Router tests
│   │   └── test_workflow_routes.py      # Workflow routes tests
│   └── schemas/        # Schema validation tests
├── core/              # Core component tests
│   ├── test_config.py  # Configuration tests
│   └── test_monitor.py # Monitoring tests
├── utils/            # Utility function tests
└── integration/      # Integration tests
```

## Test Types

### Unit Tests
- Located in the same directory as the code being tested
- Test individual functions and methods
- Use mocks and stubs for dependencies
- Fast and isolated

### Integration Tests
- Located in the `integration` directory
- Test interactions between components
- Use real dependencies where possible
- Verify system behavior

### Test Naming Conventions
- Use descriptive names that indicate the test purpose
- Follow the pattern `test_[feature]_[scenario].py`
- Use docstrings to describe test cases

## Running Tests

### All Tests
```bash
python -m pytest tests/ -v -s
```

### Specific Test Files
```bash
python -m pytest tests/api/middleware/test_security_middleware.py -v -s
```

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.security` - Security-related tests
- `@pytest.mark.performance` - Performance tests

## Test Fixtures

Common fixtures are defined in `conftest.py`:
- `mock_settings` - Mock configuration
- `mock_monitor` - Mock monitoring
- `test_client` - FastAPI test client
- `security_middleware` - Security middleware instance

## Best Practices

1. Write clear, descriptive test names
2. Use fixtures for common setup
3. Mock external dependencies
4. Keep tests independent
5. Use markers for test categorization
6. Include proper error messages
7. Test both success and failure cases
8. Use parameterized tests for multiple scenarios
