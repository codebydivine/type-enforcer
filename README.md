# Type Enforcer

[![PyPI version](https://badge.fury.io/py/divine-type-enforcer.svg)](https://badge.fury.io/py/divine-type-enforcer)
[![Python versions](https://img.shields.io/pypi/pyversions/divine-type-enforcer.svg)](https://pypi.org/project/divine-type-enforcer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/divinescreener/type-enforcer)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A blazing-fast runtime type validation library for Python 3.13+ that bridges the gap between static type hints and runtime safety. Perfect for validating API responses, user inputs, configurations, and any external data entering your application.

## 🚀 Why Type Enforcer?

### The Challenge

Python's type hints are powerful but only enforced during development. At runtime, your carefully typed code can still receive incorrectly structured data, leading to:

- **Silent Failures**: Incorrect data types causing subtle bugs deep in your code
- **Poor Error Messages**: Generic `AttributeError` or `TypeError` that don't explain what went wrong
- **Security Risks**: Unvalidated external input potentially breaking your application logic
- **Debugging Nightmares**: Hours spent tracking down where bad data entered your system

### Our Solution

Type Enforcer provides **bulletproof runtime validation** with:

```python
# Without Type Enforcer - Runtime explosion 💥
def process_user(user_data: dict) -> str:
    # This might fail deep in your code with a cryptic error
    return f"Welcome {user_data['name'].upper()}, age {user_data['age']}"

# With Type Enforcer - Safe and validated ✅
from type_enforcer import enforce
from typing import TypedDict

class User(TypedDict):
    name: str
    age: int

def process_user(user_data: dict) -> str:
    # Validates structure and types before processing
    user = enforce(user_data, User)
    return f"Welcome {user.name.upper()}, age {user.age}"
```

## ✨ Features

- 🎯 **Runtime Type Validation**: Enforce type constraints when it matters most - at runtime
- 🔍 **Crystal Clear Errors**: Path-based error messages like `data.users[0].email: Expected str, got int`
- 🏗️ **Complex Type Support**: TypedDict, dataclass, Union, Literal, Enum, and all standard types
- 🔄 **Smart Type Conversion**: Automatically converts compatible types (dict → dataclass, str → enum)
- ⚡ **Optimized Performance**: Intelligent caching for repeated validations
- 🐍 **Modern Python**: Built for Python 3.13+ with full support for new syntax like `X | Y` unions
- ✅ **Battle-Tested**: 100% test coverage with extensive edge case handling

## 📦 Installation

```bash
# Using pip
pip install divine-type-enforcer

# Using uv
uv add divine-type-enforcer

# For development
git clone https://github.com/divine/type-enforcer
cd type-enforcer
uv sync
```

### Requirements
- Python 3.13+
- No external dependencies! 🎉

## 🚀 Quick Start

```python
from type_enforcer import enforce, ValidationError
from typing import TypedDict, Optional

class UserProfile(TypedDict):
    username: str
    email: str
    age: int
    is_active: bool
    metadata: Optional[dict[str, str]]

# Validate API response
try:
    response_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "age": 30,
        "is_active": True,
        "metadata": {"role": "admin"}
    }

    user = enforce(response_data, UserProfile)
    print(f"Validated user: {user['username']}")

except ValidationError as e:
    print(f"Validation failed: {e}")
```

## 📖 Usage Examples

### Basic Type Validation

```python
from type_enforcer import enforce, ValidationError

# Simple types
enforce(42, int)                    # ✅ Returns: 42
enforce(3.14, float)                # ✅ Returns: 3.14
enforce("hello", str)               # ✅ Returns: "hello"
enforce(True, bool)                 # ✅ Returns: True

# Type mismatches raise ValidationError
try:
    enforce("not a number", int)
except ValidationError as e:
    print(e)  # ": Expected int, got str"
```

### Collections and Nested Structures

```python
from typing import List, Dict, Tuple

# Lists with type checking
users = ["Alice", "Bob", "Charlie"]
enforce(users, List[str])           # ✅ Valid

numbers = [1, 2, "three"]
try:
    enforce(numbers, List[int])
except ValidationError as e:
    print(e)  # "[2]: Expected int, got str"

# Nested dictionaries
config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "user": "admin",
            "password": "secret"
        }
    }
}

ConfigType = Dict[str, Dict[str, int | str | Dict[str, str]]]
enforce(config, ConfigType)         # ✅ Valid

# Fixed-length tuples
point = (10, 20)
enforce(point, Tuple[int, int])     # ✅ Returns: (10, 20)

# Variable-length tuples
numbers = (1, 2, 3, 4, 5)
enforce(numbers, Tuple[int, ...])   # ✅ Valid
```

### Advanced Type Validation

```python
from typing import Union, Optional, Literal
from enum import Enum
from dataclasses import dataclass

# Union types (including new | syntax)
enforce(42, int | str)              # ✅ Returns: 42
enforce("hello", int | str)         # ✅ Returns: "hello"

# Optional types
enforce(None, Optional[str])        # ✅ Returns: None
enforce("value", Optional[str])     # ✅ Returns: "value"

# Literal types
enforce("small", Literal["small", "medium", "large"])  # ✅ Valid

# Enums with automatic conversion
class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

enforce("PENDING", Status)          # ✅ Returns: Status.PENDING
enforce(Status.APPROVED, Status)    # ✅ Returns: Status.APPROVED

# Dataclasses with dict conversion
@dataclass
class Point:
    x: float
    y: float

enforce({"x": 10, "y": 20}, Point)  # ✅ Returns: Point(x=10.0, y=20.0)
```

### Real-World Example: API Response Validation

```python
from typing import TypedDict, Optional, List
from datetime import datetime
from type_enforcer import enforce, ValidationError

class Address(TypedDict):
    street: str
    city: str
    country: str
    postal_code: Optional[str]

class UserResponse(TypedDict):
    id: int
    username: str
    email: str
    created_at: str
    is_verified: bool
    profile: dict[str, str | int]
    addresses: List[Address]
    tags: Optional[List[str]]

# Simulated API response
api_response = {
    "id": 12345,
    "username": "jane_doe",
    "email": "jane@example.com",
    "created_at": "2024-01-15T10:30:00Z",
    "is_verified": True,
    "profile": {
        "age": 28,
        "bio": "Software engineer",
        "location": "San Francisco"
    },
    "addresses": [
        {
            "street": "123 Main St",
            "city": "San Francisco",
            "country": "USA",
            "postal_code": "94105"
        }
    ],
    "tags": ["developer", "python", "ai"]
}

try:
    # Validate the entire response structure
    validated_user = enforce(api_response, UserResponse)

    # Now you can safely access all fields
    print(f"User {validated_user['username']} joined on {validated_user['created_at']}")
    print(f"Primary city: {validated_user['addresses'][0]['city']}")

except ValidationError as e:
    # Detailed error showing exact path to the problem
    print(f"API response validation failed: {e}")
    # Example error: "addresses[0].postal_code: Expected str | None, got int"
```

### Configuration File Validation

```python
from typing import TypedDict, Literal, Optional

class DatabaseConfig(TypedDict):
    host: str
    port: int
    username: str
    password: str
    database: str
    pool_size: Optional[int]

class LoggingConfig(TypedDict):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    format: str
    file: Optional[str]

class AppConfig(TypedDict):
    environment: Literal["development", "staging", "production"]
    debug: bool
    database: DatabaseConfig
    logging: LoggingConfig
    features: dict[str, bool]

# Load configuration (from JSON, YAML, etc.)
config_data = {
    "environment": "production",
    "debug": False,
    "database": {
        "host": "db.example.com",
        "port": 5432,
        "username": "app_user",
        "password": "secure_password",
        "database": "myapp",
        "pool_size": 20
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "/var/log/myapp.log"
    },
    "features": {
        "new_ui": True,
        "beta_api": False,
        "analytics": True
    }
}

# Validate configuration on startup
try:
    config = enforce(config_data, AppConfig)
    print(f"✅ Configuration valid for {config['environment']} environment")
except ValidationError as e:
    print(f"❌ Configuration error: {e}")
    exit(1)
```

## 🛡️ Error Handling

Type Enforcer provides detailed, actionable error messages:

```python
from type_enforcer import enforce, ValidationError
from typing import TypedDict, List

class Product(TypedDict):
    id: int
    name: str
    price: float
    tags: List[str]

# Example with multiple errors
invalid_data = {
    "id": "not-a-number",  # Wrong type
    "name": "Laptop",
    "price": "2999.99",    # String instead of float
    "tags": ["electronics", 123, "computers"]  # Mixed types
}

try:
    enforce(invalid_data, Product)
except ValidationError as e:
    print(f"Validation error: {e}")
    # Output: "id: Expected int, got str"

    # The error message pinpoints the exact location of the first error
```

## 🎯 Best Practices

### 1. Validate at System Boundaries

```python
from type_enforcer import enforce
from typing import TypedDict

class RequestPayload(TypedDict):
    action: str
    data: dict[str, any]

@app.route("/api/process", methods=["POST"])
def process_request():
    try:
        # Validate incoming data immediately
        payload = enforce(request.json, RequestPayload)
        return handle_action(payload["action"], payload["data"])
    except ValidationError as e:
        return {"error": f"Invalid request: {e}"}, 400
```

### 2. Create Reusable Type Definitions

```python
# types.py
from typing import TypedDict, Optional, Literal

class Money(TypedDict):
    amount: float
    currency: Literal["USD", "EUR", "GBP"]

class BaseEntity(TypedDict):
    id: int
    created_at: str
    updated_at: str

class User(BaseEntity):
    email: str
    name: str
    balance: Money
    preferences: Optional[dict[str, any]]
```

### 3. Combine with Default Values

```python
from type_enforcer import enforce
from typing import TypedDict, Optional

class Settings(TypedDict, total=False):
    theme: Literal["light", "dark"]
    notifications: bool
    language: str

DEFAULT_SETTINGS: Settings = {
    "theme": "light",
    "notifications": True,
    "language": "en"
}

def load_user_settings(user_data: dict) -> Settings:
    # Merge with defaults and validate
    settings = {**DEFAULT_SETTINGS, **user_data}
    return enforce(settings, Settings)
```

## 🔧 Development

### Setup

```bash
# Clone the repository
git clone https://github.com/divinescreener/type-enforcer
cd type-enforcer

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run mypy src
```

### Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

Key points:
- Maintain 100% test coverage
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

## 📊 Performance

Type Enforcer is designed for performance:

- **Caching**: Type introspection results are cached for repeated validations
- **Early Exit**: Validation stops at the first error for efficiency
- **Minimal Dependencies**: Zero external dependencies means fast imports
- **Optimized Paths**: Common types (int, str, etc.) use fast paths

## 🔒 Security

- Safe for validating untrusted input
- No code execution during validation
- No arbitrary object instantiation
- Memory-efficient for large data structures

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built for the modern Python ecosystem
- Inspired by the need for runtime type safety in production applications
- Special thanks to the Python typing community

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/divinescreener">DIVINE</a>
</p>
