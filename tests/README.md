# Tests Directory

## Overview
This directory contains automated tests for the Yo-Yo Elite Soccer AI Coach platform.

## Running Tests

### Run all tests
```bash
cd /app
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Backend tests
pytest -m backend

# Slow tests (skip by default)
pytest -m "not slow"
```

### Run with coverage
```bash
pytest --cov=backend --cov-report=html
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Pytest configuration and fixtures
├── README.md             # This file
├── unit/                 # Unit tests (fast, isolated)
│   ├── test_models.py
│   └── test_utils.py
├── integration/          # Integration tests (API, DB)
│   ├── test_auth_api.py
│   └── test_assessment_api.py
└── e2e/                  # End-to-end tests (full workflows)
    └── test_player_journey.py
```

## Writing Tests

### Test naming conventions
- File names: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Using fixtures
```python
def test_example(backend_url, test_user_credentials):
    # Use fixtures from conftest.py
    pass
```

### Marking tests
```python
import pytest

@pytest.mark.unit
def test_unit_example():
    pass

@pytest.mark.integration
@pytest.mark.backend
def test_api_example():
    pass

@pytest.mark.slow
def test_slow_example():
    pass
```

## Test Scripts vs Real Tests

**Tests (this directory)**:
- Automated, repeatable
- No manual intervention
- Fast execution
- Runnable in CI/CD

**Scripts (`/app/scripts/`)**:
- Manual testing
- Debugging utilities
- One-off validations
- Interactive exploration

## Prerequisites

### Install test dependencies
```bash
cd /app/backend
pip install pytest pytest-cov pytest-asyncio
```

### Start services
Tests may require backend services running:
```bash
sudo supervisorctl start all
```

## CI/CD Integration

These tests are designed to run in automated pipelines:
```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    cd /app
    pytest --junitxml=test-results.xml
```

## Troubleshooting

### Tests not discovered
- Check file naming matches `test_*.py`
- Ensure `__init__.py` exists in test directories
- Verify `pytest.ini` configuration

### Import errors
- Check `conftest.py` has correct path setup
- Ensure backend dependencies installed

### Connection errors
- Verify services are running: `sudo supervisorctl status`
- Check backend URL in fixtures

## Contributing

When adding new tests:
1. Place in appropriate category (unit/integration/e2e)
2. Use existing fixtures from `conftest.py`
3. Mark tests with appropriate decorators
4. Keep tests fast and isolated
5. Add docstrings explaining test purpose
