#!/bin/bash
# Setup script for pre-commit hooks

echo "Setting up pre-commit hooks for divine-type-enforcer..."

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dev dependencies (including pre-commit)
echo "Installing dev dependencies with Poetry..."
poetry install

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
poetry run pre-commit install

# Run pre-commit on all files to show what it will do
echo "Running pre-commit on all files (this will show and fix any formatting issues)..."
poetry run pre-commit run --all-files

echo ""
echo "✅ Pre-commit hooks are now installed!"
echo ""
echo "From now on, every time you commit:"
echo "  - Ruff will automatically fix code style issues"
echo "  - Ruff formatter will format your code"
echo "  - MyPy will check types"
echo "  - Various file checks will run"
echo ""
echo "To manually run pre-commit: poetry run pre-commit run --all-files"
echo "To bypass pre-commit (not recommended): git commit --no-verify"
