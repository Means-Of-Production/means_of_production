# Means of Production

Domain logic and objects in Python for the Means Of Production project

# setup
Have `uv` installed.  If you don't have it, `asdf` can install it.

`uv venv`

`uv sync --all-groups`

# tools
## Testing
Pytest
in the base of the repo, run `pytest`

## Type checking
We currently have both `ty` and `pyright`, while deprecating the latter

To test types, run
`uv run ty check`

