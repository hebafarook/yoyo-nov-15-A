# Testing Guide - Yo-Yo Elite Soccer AI Coach

## Overview

This document describes the complete testing strategy, structure, and procedures for the Yo-Yo Elite Soccer AI Coach platform.

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_models.py         # Domain model validation
│   └── test_auth_service.py   # Auth service business logic
└── integration/                # Integration tests (API, DB)
    ├── __init__.py
    ├── test_auth_api.py        # Auth API endpoints
    └── test_repositories.py    # Database operations
```

---

## Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation

**Characteristics**:
- ✅ Fast execution (< 0.1s per test)
- ✅ No external dependencies
- ✅ Mock all I/O operations
- ✅ Test business logic only

**What to test**:
- Domain model validation
- Service business logic
- Pure functions and utilities
- Error handling

**Example**:
```python
def test_user_create_valid():
    \"\"\"Test creating a valid user model.\"\"\"
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        role="player"
    )
    assert user.username == "testuser"
    assert user.role == "player"
```

---

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test component interactions

**Characteristics**:
- ⏱️ Slower execution (< 5s per test)
- 🔌 Uses real dependencies (DB, API)
- 🧪 Tests actual behavior
- 🔄 Requires cleanup

**What to test**:
- API endpoints (HTTP requests/responses)
- Database operations (CRUD)
- Repository layer
- Authentication flow

**Example**:
```python
@pytest.mark.asyncio
async def test_register_endpoint(api_url, unique_user_data):
    \"\"\"Test user registration API endpoint.\"\"\"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{api_url}/auth-v2/register",
            json=unique_user_data
        )
        assert response.status_code == 201
        assert "token" in response.json()
```

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Ensure backend services are running (for integration tests)
sudo supervisorctl status backend
```

---

### Quick Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test category
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m backend           # Backend tests only

# Run specific test file
pytest tests/unit/test_models.py
pytest tests/integration/test_auth_api.py

# Run specific test class
pytest tests/unit/test_models.py::TestUserModels

# Run specific test function
pytest tests/unit/test_models.py::TestUserModels::test_user_create_valid

# Run tests matching pattern
pytest -k "user"            # All tests with 'user' in name
pytest -k "auth and not slow"  # Auth tests, skip slow ones

# Skip slow tests
pytest -m "not slow"

# Run quietly (less output)
pytest -q

# Show test durations
pytest --durations=10       # Show 10 slowest tests
```

---

### Coverage Reports

```bash
# Run tests with coverage
pytest --cov=backend --cov-report=term

# Generate HTML coverage report
pytest --cov=backend --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser

# Coverage with missing lines
pytest --cov=backend --cov-report=term-missing
```

---

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Run tests in parallel (auto-detect CPUs)
pytest -n auto
```

---

## Test Markers

Tests are categorized using pytest markers:

```python
@pytest.mark.unit
def test_something():
    \"\"\"Unit test - fast, isolated.\"\"\"
    pass

@pytest.mark.integration
@pytest.mark.backend
async def test_api():
    \"\"\"Integration test - tests API endpoint.\"\"\"
    pass

@pytest.mark.slow
def test_heavy_operation():
    \"\"\"Slow test - may take > 1 second.\"\"\"
    pass
```

**Run specific markers**:
```bash
pytest -m unit                    # Unit tests only
pytest -m "integration and backend"  # Integration backend tests
pytest -m "not slow"              # Skip slow tests
```

---

## Writing Tests

### Test Structure (AAA Pattern)

```python
def test_something():
    # Arrange - Setup test data
    user_data = UserCreate(
        username="test",
        email="test@example.com",
        password="pass123"
    )
    
    # Act - Execute the operation
    result = create_user(user_data)
    
    # Assert - Verify the outcome
    assert result.username == "test"
    assert result.email == "test@example.com"
```

---

### Using Fixtures

```python
@pytest.fixture
def sample_user():
    \"\"\"Fixture providing sample user data.\"\"\"
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }

def test_with_fixture(sample_user):
    \"\"\"Test using fixture.\"\"\"
    assert sample_user["username"] == "testuser"
```

**Available fixtures** (from `conftest.py`):
- `backend_url` - Backend URL
- `api_base_url` - API base URL
- `test_user_data` - Sample user data
- `sample_assessment_data` - Sample assessment
- `mock_llm_response` - Mocked AI response

---

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_operation():
    \"\"\"Test async function.\"\"\"
    result = await some_async_function()
    assert result is not None
```

---

### Mocking External Dependencies

```python
from unittest.mock import Mock, AsyncMock, patch

def test_with_mock():
    \"\"\"Test with mocked dependency.\"\"\"
    # Mock repository
    mock_repo = Mock()
    mock_repo.find_by_email = AsyncMock(return_value=None)
    
    # Use mock
    service = AuthService()
    service.user_repo = mock_repo
    
    # Test
    result = await service.some_method()
    
    # Verify mock was called
    mock_repo.find_by_email.assert_called_once()
```

---

### Parametrized Tests

```python
@pytest.mark.parametrize(\"age,expected\", [
    (10, True),   # Valid age
    (5, False),   # Too young
    (35, False),  # Too old
])
def test_age_validation(age, expected):
    \"\"\"Test age validation with multiple inputs.\"\"\"
    result = validate_age(age)
    assert result == expected
```

---

## Test Data

### Unique Test Data

For integration tests, always use unique data to avoid conflicts:

```python
@pytest.fixture
def unique_user_data():
    \"\"\"Generate unique user data.\"\"\"
    timestamp = datetime.now().strftime(\"%Y%m%d%H%M%S\")
    return {
        \"username\": f\"testuser_{timestamp}\",
        \"email\": f\"test_{timestamp}@example.com\",
        \"password\": \"testpass123\"
    }
```

---

### Test Database

Integration tests should use a separate test database:

```python
@pytest.fixture(scope=\"module\")
async def test_db():
    \"\"\"Setup test database.\"\"\"
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_soccer_db']  # Use test database
    
    yield db
    
    # Cleanup
    await client.drop_database('test_soccer_db')
    client.close()
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pytest pytest-asyncio pytest-cov httpx
    
    - name: Run tests
      run: |
        cd /app
        pytest --cov=backend --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## Test Coverage Goals

### Target Coverage

- **Overall**: > 80%
- **Critical paths**: > 90%
  - Authentication
  - User registration
  - Assessment creation
  - Payment processing (if applicable)
- **Business logic**: > 85%
  - Services layer
  - Domain models
- **API routes**: > 70%
  - HTTP endpoints

### Current Coverage

Run to see current coverage:
```bash
pytest --cov=backend --cov-report=term
```

---

## Troubleshooting

### Tests Not Discovered

**Problem**: `pytest` finds 0 tests

**Solutions**:
1. Check file naming: `test_*.py` or `*_test.py`
2. Check function naming: `test_*`
3. Verify `__init__.py` exists in test directories
4. Check `pytest.ini` configuration

```bash
# Debug test discovery
pytest --collect-only
```

---

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'domain'`

**Solutions**:
1. Ensure `conftest.py` adds backend to path
2. Run from project root: `cd /app && pytest`
3. Install backend as package: `pip install -e backend/`

---

### Async Test Failures

**Problem**: `RuntimeError: no running event loop`

**Solutions**:
1. Add `@pytest.mark.asyncio` decorator
2. Check `pytest.ini` has `asyncio_mode = auto`
3. Install `pytest-asyncio`: `pip install pytest-asyncio`

---

### Database Connection Errors

**Problem**: Tests fail with database connection errors

**Solutions**:
1. Ensure MongoDB is running: `sudo service mongodb status`
2. Check MONGO_URL environment variable
3. Use test database (not production)
4. Ensure test cleanup runs

---

### Flaky Tests

**Problem**: Tests pass sometimes, fail other times

**Solutions**:
1. Check for shared state between tests
2. Ensure proper cleanup (use fixtures)
3. Mock external dependencies (AI, APIs)
4. Use unique test data (timestamps)
5. Add proper async/await

---

## Best Practices

### DO ✅

- ✅ Write deterministic tests (same input → same output)
- ✅ Mock external services (AI, payment APIs)
- ✅ Use fixtures for setup/teardown
- ✅ Keep tests independent
- ✅ Test error cases
- ✅ Use descriptive test names
- ✅ Follow AAA pattern (Arrange, Act, Assert)
- ✅ Clean up test data

### DON'T ❌

- ❌ Rely on test execution order
- ❌ Use production database
- ❌ Test external APIs directly
- ❌ Write tests with side effects
- ❌ Skip cleanup
- ❌ Test framework code
- ❌ Write slow unit tests
- ❌ Print instead of assert

---

## Migration from Manual Scripts

### Before (Manual Script)

```python
# scripts/backend_test.py
def run_test():
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(\"✅ Test passed\")
    else:
        print(\"❌ Test failed\")
```

### After (Pytest)

```python
# tests/integration/test_api.py
@pytest.mark.integration
async def test_endpoint(api_url):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        assert response.status_code == 200
```

**Key differences**:
- ❌ Print → ✅ Assert
- ❌ Manual verification → ✅ Automatic
- ❌ Sync requests → ✅ Async httpx
- ❌ Hardcoded URL → ✅ Fixture

---

## Quick Reference

### Common Assertions

```python
# Equality
assert x == y
assert x != y

# Truthiness
assert x
assert not x
assert x is None
assert x is not None

# Membership
assert x in [1, 2, 3]
assert \"key\" in dict

# Exceptions
with pytest.raises(ValueError):
    function_that_raises()

# Approximate equality (floats)
assert 0.1 + 0.2 == pytest.approx(0.3)

# String matching
assert \"hello\" in message
assert message.startswith(\"Hi\")
```

### Common Fixtures

```python
# Function scope (default)
@pytest.fixture
def data():
    return {\"key\": \"value\"}

# Class scope
@pytest.fixture(scope=\"class\")
def shared_resource():
    return Resource()

# Module scope
@pytest.fixture(scope=\"module\")
def db_connection():
    conn = connect()
    yield conn
    conn.close()

# Session scope
@pytest.fixture(scope=\"session\")
def app():
    return create_app()
```

---

## Additional Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **HTTPx**: https://www.python-httpx.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/

---

**Last Updated**: November 2024  
**Maintained By**: Yo-Yo Elite Soccer AI Coach Development Team
