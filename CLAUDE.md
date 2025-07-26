# CLAUDE.md - Repository Development Guidelines

This document contains the essential development patterns, tools, and best practices for this repository. **Read this first** to understand the codebase conventions and standards.

## 🛠️ Core Development Stack

### **Package Management: uv**
- **Always use `uv`** instead of `pip` or `poetry`
- Installation: `uv sync` (not `pip install -r requirements.txt`)
- Running commands: `uv run <command>` (not direct command execution)
- Add dependencies: `uv add <package>` (not `pip install`)

```bash
# ✅ Correct
uv sync
uv run pytest
uv run mypy src/
uv add new-package

# ❌ Incorrect  
pip install -r requirements.txt
pytest
mypy src/
pip install new-package
```

### **Python Version: 3.13+**
- **Minimum Python 3.13** required
- Use modern Python features (match statements, improved type hints, etc.)
- CLI commands: **Always use `python3`** (not `python`)

```bash
# ✅ Correct
python3 -m venv .venv
python3 script.py

# ❌ Incorrect
python -m venv .venv  
python script.py
```

## 🔧 Code Quality Tools

### **Linting: ruff**
- **Primary linter and formatter**: ruff (not flake8, black, or isort)
- Auto-fix enabled in configuration
- Line length: 120 characters
- Always fix linting issues before committing

```bash
# Format code
uv run ruff format

# Check and auto-fix issues
uv run ruff check --fix

# Check only (no fixes)
uv run ruff check
```

### **Type Checking: mypy**
- **Strict typing enabled** 
- Type annotations required for all functions
- `--strict` mode enabled in configuration
- Source path: `src/` directory structure

```bash
# Type checking
uv run mypy src/

# Check specific module
uv run mypy src/module_name/
```

### **Testing: pytest**
- **Test framework**: pytest with asyncio support
- Coverage reporting enabled
- Test directory: `tests/`
- **Async tests**: Use pytest-asyncio (configured in `asyncio_mode = "auto"`)

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_specific.py
```

## ⚡ Async Programming: anyio

### **Use anyio (NOT asyncio)**
- **Always import `anyio`** instead of `asyncio`
- Task groups: `anyio.create_task_group()` (not `asyncio.gather()`)
- Running async code: `anyio.run(main)` (not `asyncio.run(main())`)
- Subprocess: `anyio.run_process()` (not `asyncio.create_subprocess_exec()`)

```python
# ✅ Correct
import anyio

async def main():
    async with anyio.create_task_group() as tg:
        tg.start_task(task1)
        tg.start_task(task2)

anyio.run(main)

# ❌ Incorrect
import asyncio

async def main():
    await asyncio.gather(task1(), task2())

asyncio.run(main())
```

### **Task Group Pattern**
```python
# Parallel execution with anyio
async with anyio.create_task_group() as tg:
    for item in items:
        async def process_item(data=item):
            result = await process(data)
            results[data.id] = result
        
        tg.start_task(process_item)
```

## 📁 Project Structure

### **Source Directory**: `src/`
- Main code in `src/package_name/` 
- Tests in `tests/`
- Examples in `examples/`
- Documentation in root or `docs/`

### **Import Patterns**
```python
# ✅ Correct - absolute imports from src
from package_name.module import Class
from package_name.interfaces import Interface

# ❌ Incorrect - relative imports in main code
from .module import Class
from ..interfaces import Interface
```

## 🏗️ Development Workflow

### **Setup New Environment**
```bash
git clone <repository>
cd <repository>
uv sync                    # Install dependencies
uv run pytest            # Run tests
uv run ruff check        # Check linting
uv run mypy src/         # Type checking
```

### **Pre-Commit Checklist**
1. **Linting**: `uv run ruff check --fix`
2. **Formatting**: `uv run ruff format`  
3. **Type checking**: `uv run mypy src/`
4. **Tests**: `uv run pytest`
5. **All checks passing**: Commit only when green

### **Configuration Files**
- `pyproject.toml` - Central configuration (dependencies, tools, build)
- `README.md` - Project documentation and examples
- `.env` - Environment variables (local, not committed)
- `.gitignore` - Git ignore patterns

## 🎯 Code Standards

### **Type Annotations**
- **Required for all functions** and methods
- Use modern type hints (`list[str]` not `List[str]`)
- Import types from `typing` when needed
- Use `Any` sparingly, prefer specific types

```python
# ✅ Correct
def process_data(items: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    pass

# ❌ Incorrect
def process_data(items):
    pass
```

### **Error Handling**
- Use try/except blocks appropriately
- Log errors with structured logging
- Return meaningful error messages
- Don't silence exceptions without good reason

### **Documentation**
- Docstrings for public functions and classes
- Type hints serve as inline documentation
- README.md with usage examples
- Keep documentation up to date

## 🔄 Common Commands Reference

```bash
# Development setup
uv sync

# Code quality
uv run ruff format          # Format code
uv run ruff check --fix     # Fix linting issues
uv run mypy src/           # Type checking

# Testing
uv run pytest             # Run all tests
uv run pytest --cov=src   # With coverage
uv run pytest -v          # Verbose output

# Package management
uv add package-name        # Add dependency
uv add --dev package-name  # Add dev dependency
uv remove package-name     # Remove dependency

# Running scripts
uv run python3 script.py   # Run Python script
uv run python3 -m module   # Run module
```

## 📋 File Naming Conventions

- **Python files**: `snake_case.py`
- **Test files**: `test_*.py` or `*_test.py`
- **Configuration**: `pyproject.toml`, `.env`, etc.
- **Documentation**: `README.md`, `CHANGELOG.md`, etc.

## 🚨 Common Pitfalls to Avoid

1. **Don't use `asyncio`** - Always use `anyio`
2. **Don't use `python`** - Always use `python3`
3. **Don't skip type annotations** - Required for all functions
4. **Don't ignore linting errors** - Fix before committing
5. **Don't use relative imports** in main source code
6. **Don't commit without running tests** - Always test first
7. **Don't use `pip`** directly - Always use `uv`

## 🎯 Project-Specific Notes

- **License**: MIT (unless otherwise specified)
- **Python Version**: 3.13+ minimum
- **Async Library**: anyio (not asyncio)
- **Package Manager**: uv (not pip/poetry)
- **Linter**: ruff (not flake8/black)
- **Type Checker**: mypy with strict mode

## 📚 Additional Resources

- [uv documentation](https://docs.astral.sh/uv/)
- [ruff documentation](https://docs.astral.sh/ruff/)
- [anyio documentation](https://anyio.readthedocs.io/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [pytest documentation](https://docs.pytest.org/)

---

**Note**: This document should be read by anyone working on the codebase. When in doubt, follow these patterns and tools. They ensure consistency, quality, and maintainability across the project.