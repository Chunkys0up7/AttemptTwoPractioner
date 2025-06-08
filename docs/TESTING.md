# Testing Guide

## Test Structure

The test suite is organized as follows:

```
tests/
├── api/           # API endpoint tests
├── config/        # Configuration tests
├── data/          # Test data files
├── reports/       # Test reports and coverage
├── root/          # Root-level tests
├── scripts/       # Test runner scripts
└── utils/         # Test utilities and helpers
```

## Test Types

We use several types of tests:

- **Unit Tests** (`@pytest.mark.unit`): Test individual components
- **Integration Tests** (`@pytest.mark.integration`): Test component interactions
- **End-to-End Tests** (`@pytest.mark.e2e`): Test full system flows
- **Performance Tests** (`@pytest.mark.performance`): Test system performance
- **Security Tests** (`@pytest.mark.security`): Test security features
- **Accessibility Tests** (`@pytest.mark.accessibility`): Test accessibility
- **Smoke Tests** (`@pytest.mark.smoke`): Basic functionality tests
- **Regression Tests** (`@pytest.mark.regression`): Test for regressions
- **Slow Tests** (`@pytest.mark.slow`): Long-running tests
- **Flaky Tests** (`@pytest.mark.flaky`): Unstable tests
- **External Tests** (`@pytest.mark.external`): Tests requiring external services

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/api/test_security_middleware.py

# Run tests with coverage
pytest --cov=mcp --cov-report=term-missing

# Run tests with specific marker
pytest -m "unit or integration"
```

### Parallel Test Execution

```bash
# Run tests in parallel
pytest -n auto

# Run tests in parallel with specific number of processes
pytest -n 4
```

### Test Isolation

```bash
# Run tests in isolation
pytest --tb=short

# Run tests with timeout
pytest --timeout=30
```

## Test Configuration

### Environment Variables

- `TESTING=true` - Enable test mode
- `TEST_ENV` - Test environment directory
- `TEST_DATA_DIR` - Test data directory
- `TEST_REPORTS_DIR` - Test reports directory
- `RATE_LIMIT_MAX_REQUESTS` - Maximum requests per window
- `RATE_LIMIT_WINDOW` - Rate limit window in seconds

### Coverage Configuration

Coverage reports are generated in:
- `tests/reports/coverage/` - HTML coverage report
- `tests/reports/coverage/coverage.xml` - XML coverage report
- `tests/reports/coverage/coverage.json` - JSON coverage report

## Test Utilities

### Available Utilities

- `test_data.py` - Test data generation and loading
- `test_assertions.py` - Custom assertions
- `test_utils.py` - General test utilities
- `test_environment.py` - Test environment setup
- `test_validation.py` - Data validation helpers
- `test_performance.py` - Performance measurement
- `test_error.py` - Error handling tests
- `test_logging.py` - Logging utilities
- `test_database.py` - Database test utilities
- `test_monitoring.py` - Monitoring utilities
- `test_security.py` - Security test utilities

## Test Data

Test data is located in `tests/data/` and includes:
- Workflow samples
- Security samples
- Rate limiting data
- Error scenarios
- Performance test data

## Test Reports

Test reports are generated in:
- `tests/reports/logs/` - Test execution logs
- `tests/reports/coverage/` - Coverage reports
- `tests/reports/junit/` - JUnit XML reports
- `tests/reports/html/` - HTML reports

## Best Practices

1. Write clear, descriptive test names
2. Use appropriate test markers
3. Keep tests independent
4. Use fixtures for shared setup
5. Add proper assertions
6. Include test documentation
7. Follow test isolation principles
8. Use proper error handling
9. Include performance considerations
10. Maintain test data properly

## Troubleshooting

### Common Issues

1. **Test Isolation**
   - Use `@pytest.mark.isolation` for tests requiring isolation
   - Use fixtures for shared setup

2. **Performance**
   - Use `@pytest.mark.performance` for performance tests
   - Monitor test execution time

3. **Flaky Tests**
   - Use `@pytest.mark.flaky` for unstable tests
   - Add proper retries

4. **External Dependencies**
   - Mock external services
   - Use test doubles
   - Add proper timeouts
