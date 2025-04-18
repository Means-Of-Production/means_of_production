# Development Environment Setup

## Issues

### 1. Email Validation
The tests were failing with the following error:
```
ImportError: email-validator is not installed, run `pip install pydantic[email]`
```

This occurred because the `Person` class uses Pydantic's `EmailStr` type for email validation, which requires the `email-validator` package.

### 2. Missing pytest
The `pytest` command is not found even after activating the virtual environment. This is because pytest is listed as a development dependency in `pyproject.toml` but not installed by default.

## Solution
Both the `email-validator` package and `pytest` are included in the development dependencies in `pyproject.toml`.

## How to Install Development Dependencies
To install all development dependencies, run:

```bash
pdm install -G dev
```

Or if you're using pip:

```bash
pip install -e ".[dev]"
```

For uv users:
```bash
uv pip install -e ".[dev]"
```

After installing the development dependencies, you should be able to run:
```bash
pytest
```

## Alternative Solution for Email Validation
If you don't want to use email validation, you could modify the `Person` class to use `str` instead of `EmailStr` for the email field. However, this would remove the email validation functionality.
