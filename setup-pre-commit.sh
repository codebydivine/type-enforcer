#!/bin/bash
# Setup script for pre-commit hooks

echo "Setting up pre-commit hooks for divine-type-enforcer..."

# Check if UV is available
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dev dependencies (including pre-commit)
echo "Installing dev dependencies with UV..."
uv sync

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
uv run pre-commit install

# Run pre-commit on all files to show what it will do
echo "Running pre-commit on all files (this will show and fix any formatting issues)..."
uv run pre-commit run --all-files

echo ""
echo "✅ Pre-commit hooks are now installed!"
echo ""
echo "From now on, every time you commit:"
echo "  - Ruff will automatically fix code style issues"
echo "  - Ruff formatter will format your code"
echo "  - MyPy will check types"
echo "  - Various file checks will run"
echo ""
echo "To manually run pre-commit: uv run pre-commit run --all-files"
echo "To bypass pre-commit (not recommended): git commit --no-verify"
