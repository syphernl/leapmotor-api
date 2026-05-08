# Contributing to leapmotor-api

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

### Prerequisites

- Python 3.12+
- [Hatch](https://hatch.pypa.io/) (recommended) or pip

### Clone and install

```bash
git clone https://github.com/markoceri/leapmotor-api.git
cd leapmotor-api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
pytest --cov   # with coverage
```

### Linting and type checking

```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/
```

### Pre-commit hooks

```bash
pre-commit install
```

This runs `ruff` and `mypy` automatically before each commit.

## Project Structure

```
src/leapmotor_api/
├── __init__.py          # Package exports and version
├── client.py            # Synchronous API client
├── async_client.py      # Async wrapper around the sync client
├── models.py            # Dataclasses for vehicle status, signals, etc.
├── const.py             # Constants (URLs, endpoints)
├── crypto.py            # Signature and encryption utilities
├── exceptions.py        # Custom exceptions
└── image.py             # Vehicle image layer composition
```

## Pull Request Guidelines

### Before you start

- Check the [issue tracker](https://github.com/markoceri/leapmotor-api/issues) for existing issues or feature requests.
- For new features or significant changes, open an issue first to discuss the approach.

### PR requirements

- Keep changes small and focused — one concern per PR.
- Add or update tests for any new functionality.
- Ensure all checks pass: `pytest`, `ruff check`, `ruff format --check`, `mypy`.
- Follow the existing code style — the project uses [Ruff](https://github.com/astral-sh/ruff) for formatting and linting.

### Commit messages

Use [conventional commits](https://www.conventionalcommits.org/):

- `feat:` new feature or field
- `fix:` bug fix
- `docs:` documentation changes
- `chore:` maintenance, dependency updates
- `refactor:` code restructuring without behavior change
- `test:` adding or updating tests

## Code Style

- **Type annotations**: all public APIs are fully typed; the project uses `mypy --strict`.
- **Dataclasses with `slots=True`**: all model classes use `@dataclass(slots=True)`.
- **Optional fields**: vehicle status fields are `T | None` (populated only when the vehicle reports the signal).
- **Line length**: 120 characters max.
- **Imports**: sorted by `ruff` (isort-compatible).

## Adding New Vehicle Fields

When the Leapmotor API exposes new signals:

1. Add the field to the appropriate dataclass in `models.py`.
2. Add the API key → Python field mapping in the corresponding `_*_FIELDS` dict.
3. If the field comes from a signal ID, add the mapping in `_SIGNAL_TO_NAMED`.
4. Update tests in `tests/test_models.py`.
5. Update the example in `examples/usage.py`.
