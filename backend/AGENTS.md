# AGENTS.md - Coding Guidelines for Agentic Development

This document provides essential information for AI coding agents working on this FastAPI backend project. It covers build/lint/test commands, code style guidelines, and development practices.

## Project Overview

This is a FastAPI-based backend for the LASUR Platyp platform. It uses:
- Python 3.10+
- Poetry for dependency management
- PostgreSQL with SQLAlchemy/SQLModel for data persistence
- Keycloak for authentication
- Alembic for database migrations
- Pytest for testing

## Build/Lint/Test Commands

### Installation
```bash
make install          # Install dependencies with Poetry
```

### Running the Application
```bash
make run              # Start the development server with uvicorn
./start.sh            # Alternative script to start the server
```

### Database Operations
```bash
make db-upgrade       # Apply database migrations
make db-downgrade     # Revert last database migration
make db-revision      # Create new database migration (use with name="message")
```

### Testing
```bash
make test             # Run all tests with pytest
poetry run pytest tests/test_specific.py::test_function_name  # Run a specific test
poetry run pytest -k "test_name"  # Run tests matching a pattern
poetry run pytest -x  # Stop after first failure
poetry run pytest -v  # Verbose output
```

### Linting
```bash
make lint             # Run pre-commit hooks for linting
```

Note: The project uses pre-commit hooks for linting but the configuration wasn't found in the standard locations. You may need to set up pre-commit manually if contributing to the codebase.

## Code Style Guidelines

### Imports
1. Standard library imports first (sorted alphabetically)
2. Third-party imports second (sorted alphabetically)
3. Local/project imports last (sorted alphabetically)
4. Use explicit imports rather than wildcard imports
5. Group imports by category with blank lines between groups

Example:
```python
from typing import List, Dict, Optional
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text

from api.db import get_session
from api.models.domain import Company
```

### Formatting
1. Follow PEP 8 standards
2. Maximum line length: 88 characters (default Black formatting)
3. Use 4 spaces for indentation (no tabs)
4. Use double quotes for strings unless single quotes are needed to avoid escaping
5. Include trailing commas in multiline constructs

### Type Hints
1. Use type hints for all function parameters and return values
2. Prefer built-in types (list, dict) over typing.List, typing.Dict for Python 3.9+
3. Use Optional[T] for values that can be None
4. Use Union[A, B] for values that can be of different types

Example:
```python
def find_companies(
    filter: str = Query(None),
    sort: str = Query(None),
    range: str = Query("[0,99]"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(kc_service.get_user_info())
) -> CompanyResult:
```

### Naming Conventions
1. Use snake_case for variables, functions, and method names
2. Use PascalCase for class names
3. Use UPPER_CASE for constants
4. Use descriptive names that clearly indicate purpose
5. Private methods/variables start with underscore (_internal_method)

### Error Handling
1. Use HTTPException from FastAPI for API-level errors
2. Include appropriate HTTP status codes
3. Provide meaningful error messages
4. Log errors appropriately for debugging
5. Handle edge cases explicitly

Example:
```python
if not entity:
    raise HTTPException(
        status_code=404, detail="Company not found")
```

### Documentation
1. Use docstrings for all public functions, classes, and modules
2. Follow Google Python Style Guide for docstrings
3. Include type information in docstrings when not obvious
4. Document complex business logic
5. Comment non-obvious code sections

### API Design
1. Follow RESTful principles
2. Use appropriate HTTP verbs (GET, POST, PUT, DELETE)
3. Use plural nouns for collections (/companies not /company)
4. Return appropriate HTTP status codes
5. Use consistent error response format
6. Version APIs when necessary

### Database Models
1. Use SQLModel for ORM models
2. Define base classes for shared attributes
3. Use proper relationships between models
4. Include timestamps (created_at, updated_at) for auditable entities
5. Use appropriate field constraints and defaults

### Services Layer
1. Encapsulate business logic in service classes
2. Keep route handlers thin
3. Use dependency injection for session management
4. Handle authorization checks in service methods
5. Return domain models rather than database models when appropriate

### Testing
1. Use pytest for unit and integration tests
2. Follow Arrange-Act-Assert pattern
3. Use descriptive test names
4. Mock external dependencies
5. Test edge cases and error conditions
6. Use fixtures for setup/teardown

Example:
```python
def test_compute_equipments_frequencies():
    # Arrange
    df = load_test_dataframe()
    service = FrequenciesService(df)
    
    # Act
    result = service.compute_equipments_frequencies()
    
    # Assert
    assert isinstance(result, Frequencies)
    assert result.field == 'equipments'
```

## Authentication and Authorization

1. Use the provided auth middleware
2. Check permissions with decorators or service methods
3. Include user parameter in service methods when authorization is needed
4. Follow principle of least privilege

## Development Practices

1. Keep functions small and focused
2. Use meaningful variable names
3. Avoid deep nesting
4. Prefer composition over inheritance
5. Write tests for new functionality
6. Update documentation when changing APIs
7. Handle errors gracefully
8. Use logging appropriately for debugging and monitoring
9. Follow security best practices (no hardcoded secrets, proper validation)

## Project Structure

- `/api` - Main application code
  - `/models` - Database models and schemas
  - `/views` - API route definitions
  - `/services` - Business logic
  - `/utils` - Utility functions
- `/tests` - Test files
- `/migrations` - Database migration files
- `/data` - Static data files

## Environment Variables

Configuration is managed through environment variables defined in `api/config.py`. The application uses pydantic-settings for validation and type conversion.

Key variables include:
- Database connection settings (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
- Keycloak authentication settings (KEYCLOAK_REALM, KEYCLOAK_URL, etc.)
- Application-specific settings (LASUR_API_URL, PATH_PREFIX, etc.)

## Deployment Considerations

1. Run database migrations before deploying
2. Ensure environment variables are properly configured
3. Monitor application logs
4. Set appropriate timeouts and resource limits
5. Use production-ready WSGI server for deployment