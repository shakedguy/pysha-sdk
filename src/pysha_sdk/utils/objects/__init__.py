"""Object utilities module for pysha-sdk."""

import copy
import inspect
from abc import ABC
from typing import (
    Any,
    Callable,
    Collection,
    Literal,
    Mapping,
    Optional,
    Type,
    TypeAlias,
    TypeVar,
    Union,
)

from pydantic import BaseModel

# Type definitions
ValidIterables = Union[dict[str, Any], Collection[Any]]

T = TypeVar("T")
IncEx: TypeAlias = Union[
    set[int],
    set[str],
    Mapping[int, Union["IncEx", bool]],
    Mapping[str, Union["IncEx", bool]],
]

# Try to import Cython implementations for performance-critical functions
try:
    from ._native import (
        is_iterable_except_str_like_cython as _is_iterable_except_str_like,
    )
    from ._native import (
        recursive_sort_keys_cython as _recursive_sort_keys_dict,
    )

    # Wrap Cython functions to match Python API
    def is_iterable_except_str_like(obj: object) -> bool:
        return _is_iterable_except_str_like(obj)

    def recursive_sort_keys(input_value: ValidIterables) -> ValidIterables:
        """Recursively sort keys with Cython optimization for dicts."""
        import pydash as _

        if not _.is_iterable(input_value):
            raise ValueError("Invalid input, must be an iterable")

        if isinstance(input_value, dict):
            return _recursive_sort_keys_dict(input_value)

        # For collections, use Python implementation
        from ._py import _return_same_iterable
        return _return_same_iterable(
            input_value, [recursive_sort_keys(item) for item in input_value]
        )

except ImportError:
    from ._py import (
        is_iterable_except_str_like,
        recursive_sort_keys,
    )

# Always import non-optimized functions from Python implementation
from ._py import (
    ChangeKeysCase,
    dict_or_pydantic_model_to_dict,
    find_subclasses,
    model_dump,
)

__all__ = [
    "ChangeKeysCase",
    "dict_or_pydantic_model_to_dict",
    "find_subclasses",
    "is_iterable_except_str_like",
    "model_dump",
    "recursive_sort_keys",
]
