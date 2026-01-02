# pysha-sdk

A high-performance Python SDK with Cython-optimized utilities for string manipulation, cryptography, object handling, and more.

[![CI/CD](https://github.com/guysha94/pysha-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/guysha94/pysha-sdk/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/guysha94/pysha-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/guysha94/pysha-sdk)
[![PyPI version](https://badge.fury.io/py/pysha-sdk.svg)](https://badge.fury.io/py/pysha-sdk)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

## Features

- **🚀 High Performance**: Cython-optimized implementations for performance-critical operations
- **📦 Comprehensive Utilities**: String manipulation, cryptography, object handling, and more
- **🔄 Automatic Fallback**: Pure Python implementations when Cython extensions aren't available
- **✅ Well Tested**: 84% code coverage with 179+ unit tests
- **🔒 Type Safe**: Full type hints and mypy support
- **📚 Well Documented**: Comprehensive docstrings and examples

## Installation

```bash
# Using pip
pip install pysha-sdk

# Using uv (recommended)
uv pip install pysha-sdk

# With optional dependencies
pip install pysha-sdk[inflect,phonenumbers,email,bson]
```

## Quick Start

### String Utilities

```python
from pysha_sdk import (
    to_camel_case,
    to_snake_case,
    extract_digits,
    is_valid_email,
    normalize,
    slugify,
)

# Case conversion
to_camel_case("hello_world")  # "helloWorld"
to_snake_case("HelloWorld")   # "hello_world"

# String manipulation
extract_digits("abc123def")   # "123"
is_valid_email("user@example.com")  # (True, None)

# Text normalization
normalize("<p>Hello **world**!</p>")  # "Hello world!"

# URL-friendly slugs
slugify("Hello World!")  # "hello-world"
```

### Crypto Utilities

```python
from pysha_sdk import (
    hash_password,
    match_password,
    uuidv7,
    calculate_md5_hash,
    generate_random_token,
)

# Password hashing
hashed = hash_password("my_password")
match_password("my_password", hashed)  # True

# UUID generation
uuid = uuidv7()  # UUIDv7 with timestamp

# Hashing
md5_hash = calculate_md5_hash("content")  # "5d41402abc4b2a76b9719d911017c592"

# Random tokens
token = generate_random_token(32, "hex")  # 32-character hex token
```

### Object Utilities

```python
from pysha_sdk import (
    recursive_sort_keys,
    ChangeKeysCase,
    model_dump,
)
from pydantic import BaseModel

# Recursive key sorting
data = {"z": 1, "a": {"c": 2, "b": 1}}
sorted_data = recursive_sort_keys(data)
# {"a": {"b": 1, "c": 2}, "z": 1}

# Case conversion for dictionaries
ChangeKeysCase.to_camel_case({"first_name": "John"})
# {"firstName": "John"}

# Pydantic model dumping
class User(BaseModel):
    name: str
    age: int

user = User(name="John", age=30)
model_dump(user)  # {"name": "John", "age": 30}
```

### DictMixin

```python
from pysha_sdk.utils.mixins.dict_mixin import DictMixin

class MyModel(DictMixin):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

obj = MyModel(name="John", age=30)

# Dict-like access
obj["name"]  # "John"
obj["nested.deep.value"]  # Path-based access with glom

# Dict methods
list(obj.keys())  # ["name", "age"]
obj.get("missing", "default")  # "default"
```

## Modules

### String Utilities (`pysha_sdk.utils.strings`)

Comprehensive string manipulation functions:

- **Case Conversion**: `to_camel_case`, `to_snake_case`, `to_kebab_case`, `to_pascale_case`, `to_constant_case`, `to_title_case`
- **Encoding/Decoding**: `to_hex`, `from_hex`, `to_base64`, `from_base64`, `to_ascii`
- **Validation**: `is_valid_email`, `is_valid_phone_number`, `is_valid_israeli_id`, `is_cron_expression`, `is_hex`, `is_ascii`, `is_hebrew`
- **Text Processing**: `normalize`, `slugify`, `deburr`, `words`, `compounder`, `extract_digits`
- **URL Utilities**: `to_url`, `flatten_url_params`, `delimited_path_join`
- **Pluralization**: `to_plural`, `to_singular` (requires `inflect`)

### Crypto Utilities (`pysha_sdk.utils.crypto`)

Cryptographic and security functions:

- **Password Management**: `hash_password`, `encrypt_password`, `match_password`
- **Hashing**: `calculate_md5_hash`
- **UUID Generation**: `uuidv7`, `to_stable_uuid`, `uuidv7_to_datetime`
- **Random Generation**: `generate_random_id`, `generate_random_token`, `generate_unique_secure_token`

### Object Utilities (`pysha_sdk.utils.objects`)

Object and data structure manipulation:

- **Pydantic Integration**: `model_dump`, `dict_or_pydantic_model_to_dict`
- **Key Operations**: `recursive_sort_keys`, `ChangeKeysCase` (camel, snake, kebab, Pascal, constant, dot case)
- **Type Utilities**: `is_iterable_except_str_like`, `find_subclasses`

### DictMixin (`pysha_sdk.utils.mixins.dict_mixin`)

A mixin class that provides dict-like interface to objects:

- Dict-like access with `obj[key]`
- Path-based access with glom: `obj["nested.deep.value"]`
- All standard dict methods: `keys()`, `values()`, `items()`, `get()`, etc.
- Works seamlessly with Pydantic models

## Performance

This package uses Cython to optimize performance-critical operations. When Cython extensions are available, functions automatically use optimized implementations. If Cython isn't available, the package falls back to pure Python implementations.

**Optimized Functions:**
- String operations: `extract_digits`, `is_ascii`, `is_hex`, `is_hebrew`, `to_hex`, `from_hex`, `to_base64`, `from_base64`, `to_ascii`
- Crypto operations: `calculate_md5_hash`, `encrypt_password`, `match_password`, `to_stable_uuid`, `uuidv7`, `uuidv7_to_datetime`
- Object operations: `recursive_sort_keys`, `change_keys_case`, `is_iterable_except_str_like`
- DictMixin operations: All dict-like operations

## Requirements

- Python 3.13+
- Optional dependencies:
  - `inflect` - For pluralization features
  - `phonenumbers` - For phone number validation/formatting
  - `email-validator` - For email validation
  - `pymongo` - For ObjectId conversion (bson)

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/guysha94/pysha-sdk.git
cd pysha-sdk

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev

# Build the package
uv build
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ -v --cov=src/pysha_sdk --cov-report=html

# Run specific test file
uv run pytest tests/test_strings.py -v
```

### Code Quality

```bash
# Linting
uv run ruff check src/ tests/

# Formatting
uv run ruff format src/ tests/

# Type checking
uv run mypy src/pysha_sdk
```

### Building

```bash
# Build wheel and sdist
uv build

# Install locally
uv pip install dist/pysha_sdk-*.whl
```

## Project Structure

```
pysha-sdk/
├── src/
│   └── pysha_sdk/
│       ├── __init__.py          # Main package exports
│       └── utils/
│           ├── strings/         # String utilities
│           │   ├── __init__.py
│           │   ├── _native.pyx  # Cython optimizations
│           │   ├── _py.py       # Python fallback
│           │   └── regex.py    # Regex patterns
│           ├── crypto/          # Crypto utilities
│           │   ├── __init__.py
│           │   ├── _native.pyx  # Cython optimizations
│           │   └── _py.py       # Python fallback
│           ├── objects/         # Object utilities
│           │   ├── __init__.py
│           │   ├── _native.pyx  # Cython optimizations
│           │   └── _py.py       # Python fallback
│           └── mixins/
│               └── dict_mixin/  # DictMixin class
│                   ├── __init__.py
│                   ├── _native.pyx
│                   └── _py.py
├── tests/                        # Test suite
│   ├── test_strings.py
│   ├── test_crypto.py
│   ├── test_objects.py
│   ├── test_dict_mixin.py
│   └── test_strings_py_fallback.py
├── .github/
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline
├── pyproject.toml               # Project configuration
├── setup.py                     # Cython build setup
└── README.md                    # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style (enforced by ruff)
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass and coverage is maintained
- Type hints are required for all functions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**guysha94**

- Email: guy.sha@superplay.co

## Acknowledgments

- Built with [Cython](https://cython.org/) for performance
- Uses [uv](https://github.com/astral-sh/uv) for fast package management
- Inspired by lodash and similar utility libraries

## Changelog

### 0.1.0 (2024)

- Initial release
- String utilities with Cython optimizations
- Crypto utilities (password hashing, UUID generation)
- Object utilities (key sorting, case conversion)
- DictMixin for dict-like object access
- Comprehensive test suite (84% coverage)
- CI/CD pipeline with automated testing and publishing

## Support

For issues, questions, or contributions, please open an issue on [GitHub](https://github.com/guysha94/pysha-sdk/issues).
