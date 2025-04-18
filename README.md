# Means of Production

Domain logic and objects in Python for the Means Of Production project

## Development Setup

### Using uv

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1. Install dependencies:
   ```bash
   # Install only the main dependencies
   uv sync

   # Install main dependencies and development dependencies
   uv pip install -e ".[dev]"
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

3. Run tests:
   ```bash
   pytest
   ```
