# Email Validation Fix

## Issue
The tests were failing with the following error:
```
ImportError: email-validator is not installed, run `pip install pydantic[email]`
```

This occurred because the `Person` class uses Pydantic's `EmailStr` type for email validation, which requires the `email-validator` package.

## Solution
The `email-validator` package has been added to the development dependencies in `pyproject.toml`.

## How to Install
To install the new dependency, run:

```bash
pdm install -G dev
```

Or if you're using pip:

```bash
pip install email-validator
```

## Alternative Solution
If you don't want to use email validation, you could modify the `Person` class to use `str` instead of `EmailStr` for the email field. However, this would remove the email validation functionality.