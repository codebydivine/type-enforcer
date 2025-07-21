# Type Enforcer

A runtime type validation utility for Python 3.13+ with detailed error reporting.

This module provides a clean, efficient way to enforce type constraints on data,
ensuring that your function inputs, API responses, or configuration files match
the expected structure and types.

## Features

*   **Runtime Validation:** Checks types when your code runs, catching errors early.
*   **Detailed Errors:** Pinpoints exactly where validation failed in nested structures.
*   **Complex Types:** Supports `List`, `Dict`, `Tuple`, `Optional`, `Union`, `Literal`, `Enum`, `TypedDict`, and `dataclass`.
*   **Clean API:** Simple `enforce(data, expected_type)` function for easy use.
*   **Introspection Caching:** Uses caching for type analysis to improve performance.
*   **Python 3.13+:** Leverages modern Python features.
*   **100% Test Coverage:** Every line of code is thoroughly tested, ensuring reliability and stability.

## Why Type Enforcer Is Useful

### Safer Data Handling
Python's dynamic typing is flexible but can lead to runtime errors when data doesn't match expectations. Type Enforcer adds a safety layer that validates data structures at critical boundaries in your application.

### API Integration
When working with external APIs, responses may not always conform to documentation. Type Enforcer helps validate responses before your code processes them, preventing cascading errors from malformed data.

### Better Error Messages
Instead of cryptic `AttributeError` or `TypeError` deep in your processing logic, Type Enforcer provides clear, path-based error messages like `data.users[0].settings.notifications: Expected bool, got str`.

### Schema Documentation
TypedDict and dataclass definitions serve as living documentation of your data structures, making code more maintainable and self-documenting.

### Gradual Typing
While type annotations help at development time, Type Enforcer extends their value to runtime, offering a bridge between static and dynamic typing that's especially valuable at system boundaries.

### Data Transformation
Beyond validation, Type Enforcer can convert compatible types (like dictionaries to dataclasses), simplifying your data pipeline.

## Installation

```bash
# For end users
pip install divine-type-enforcer

# For development
poetry install
```

## Usage

Import the `enforce` function and use it to validate data against a type annotation:

```python
from type_enforcer import enforce, ValidationError
from typing import List, Dict, Optional, Union, Literal, TypedDict, Tuple
from enum import Enum
from dataclasses import dataclass

# Basic types
enforce(42, int)
# >> 42
enforce("hello", str)
# >> 'hello'
enforce(True, bool)
# >> True
enforce(3.14, float)
# >> 3.14
enforce(None, type(None))
# >> None

try:
    enforce("not an int", int)
except ValidationError as e:
    print(e)
# >> : Expected int, got str

# Lists
enforce([1, 2, 3], List[int])
# >> [1, 2, 3]

try:
    enforce([1, "not an int", 3], List[int])
except ValidationError as e:
    print(e)
# >> [1]: Expected int, got str

# Dictionaries
enforce({"a": 1, "b": 2}, Dict[str, int])
# >> {'a': 1, 'b': 2}

try:
    enforce({"a": 1, "b": "not an int"}, Dict[str, int])
except ValidationError as e:
    print(e)
# >> [b]: Expected int, got str

# TypedDict
class User(TypedDict):
    name: str
    age: int

enforce({"name": "Alice", "age": 30}, User)
# >> {'name': 'Alice', 'age': 30}

try:
    enforce({"name": "Alice"}, User)
except ValidationError as e:
    print(e)
# >> : Missing required keys: age

# Optional fields
enforce(None, Optional[int])
# >> None
enforce(42, Optional[int])
# >> 42

# Union types
enforce("hello", Union[int, str])
# >> 'hello'
enforce(42, Union[int, str])
# >> 42

try:
    enforce(True, Union[int, str])
except ValidationError as e:
    print(e)
# >> : Value doesn't match any type in Union. Got bool, expected one of: <class 'int'> | <class 'str'>

# Literal types
enforce("small", Literal["small", "medium", "large"])
# >> 'small'
enforce(None, Literal[None, "small", "large"])
# >> None

try:
    enforce("extra-large", Literal["small", "medium", "large"])
except ValidationError as e:
    print(e)
# >> : Expected one of: 'small', 'medium', 'large', got: 'extra-large'

# Tuples
enforce((1, 2, 3), Tuple[int, ...])
# >> (1, 2, 3)
enforce((1, "hello"), Tuple[int, str])
# >> (1, 'hello')

# Enums
class Size(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

enforce(Size.SMALL, Size)
# >> <Size.SMALL: 'small'>
enforce("SMALL", Size)  # Converts string to enum
# >> <Size.SMALL: 'small'>

try:
    enforce("EXTRA_LARGE", Size)
except ValidationError as e:
    print(e)
# >> : Invalid enum value. Valid values: SMALL, MEDIUM, LARGE

# Dataclasses
@dataclass
class Point:
    x: int
    y: int

enforce(Point(1, 2), Point)
# >> Point(x=1, y=2)
enforce({"x": 1, "y": 2}, Point)  # Converts dict to dataclass
# >> Point(x=1, y=2)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

The project maintains 100% test coverage, which helps ensure stability and correctness as new features are added. Any contributions should include appropriate tests to maintain this coverage level.

## Real-World Examples

Check out the `examples/` directory for real-world use cases of type-enforcer:

### API Response Validation

See [`examples/api_response_validation.py`](examples/api_response_validation.py) for a comprehensive example of validating complex API responses. This example shows how to:

- Define nested TypedDict structures for complex JSON responses
- Validate responses against these structures
- Handle validation errors gracefully
- Work with deeply nested optional fields

This pattern is especially useful when working with third-party APIs where you need to ensure the response matches your expected structure before processing it further.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
