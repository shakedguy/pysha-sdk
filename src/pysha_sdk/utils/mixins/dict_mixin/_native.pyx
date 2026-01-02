# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
"""
Cython implementation of performance-critical DictMixin operations.

This module contains optimized Cython implementations for hot paths
in dict mixin operations using C-level optimizations.
"""

cimport cython
from cpython.dict cimport PyDict_Check, PyDict_Contains, PyDict_Size
from cpython.object cimport PyObject_HasAttr, PyObject_SetAttr
from cpython.unicode cimport PyUnicode_Check

cpdef object dict_mixin_getitem_fast(dict obj_dict, str key):
    """
    Fast path-based dictionary access with optimized simple key lookup.

    For simple keys (no dots), uses direct dict lookup.
    For complex paths, falls back to glom.

    Args:
        obj_dict: Dictionary from vars(self).
        key: Key or path to access.

    Returns:
        Value from dictionary.
    """
    # Fast path: simple key (no dots) - direct lookup
    if '.' not in key:
        if key in obj_dict:
            return obj_dict[key]
        raise KeyError(key)

    # Complex path - use glom (import here to avoid circular dependency)
    from glom import glom
    return glom(obj_dict, key)


cpdef object dict_mixin_get_fast(dict obj_dict, str key, object default=None):
    """
    Fast get operation with optimized simple key lookup.

    Args:
        obj_dict: Dictionary from vars(self).
        key: Key or path to access.
        default: Default value if key not found.

    Returns:
        Value from dictionary or default.
    """
    # Fast path: simple key (no dots) - direct lookup
    if '.' not in key:
        if key in obj_dict:
            return obj_dict[key]
        return default

    # Complex path - use glom with exception handling
    try:
        from glom import glom
        return glom(obj_dict, key)
    except (KeyError, AttributeError):
        return default


cpdef bint dict_mixin_contains_fast(dict obj_dict, object key):
    """
    Fast contains check for dictionary.

    Args:
        obj_dict: Dictionary from vars(self).
        key: Key to check.

    Returns:
        True if key exists, False otherwise.
    """
    return key in obj_dict


cpdef bint dict_mixin_has_attr_fast(object obj, str key):
    """
    Fast attribute check using C-level hasattr.

    Args:
        obj: Object to check.
        key: Attribute name to check.

    Returns:
        True if attribute exists, False otherwise.
    """
    return PyObject_HasAttr(obj, key)


cpdef dict dict_mixin_get_vars_without_data(object obj):
    """
    Fast vars() retrieval with "data" key removal.

    Args:
        obj: Object to get vars from.

    Returns:
        Dictionary without "data" key.
    """
    cdef dict v = vars(obj)
    cdef dict result = {}
    cdef object key, value

    # Fast iteration and filtering
    for key, value in v.items():
        if key != "data":
            result[key] = value

    return result


cpdef dict dict_mixin_dir_fast(object obj):
    """
    Fast __dir__ implementation filtering out methods.

    Args:
        obj: Object to get directory from.

    Returns:
        Dictionary of non-method attributes.
    """
    from inspect import ismethod
    cdef dict v = vars(obj)
    cdef dict result = {}
    cdef object key, value

    # Fast iteration and filtering
    for key, value in v.items():
        if not ismethod(value):
            result[key] = value

    return result


cpdef void dict_mixin_clear_fast(object obj):
    """
    Fast clear operation setting all attributes to None.

    Args:
        obj: Object to clear.
    """
    cdef dict v = vars(obj)
    cdef object key

    # Fast iteration and setattr
    for key in v:
        PyObject_SetAttr(obj, key, None)


cpdef Py_ssize_t dict_mixin_len_fast(dict obj_dict):
    """
    Fast length calculation for dictionary.

    Args:
        obj_dict: Dictionary from vars(self).

    Returns:
        Length of dictionary.
    """
    return PyDict_Size(obj_dict)


cpdef object dict_mixin_keys_fast(object obj):
    """
    Fast keys() operation with "data" key removal.

    Args:
        obj: Object to get keys from.

    Returns:
        KeysView without "data" key.
    """
    cdef dict result = dict_mixin_get_vars_without_data(obj)
    return result.keys()


cpdef object dict_mixin_values_fast(object obj):
    """
    Fast values() operation with "data" key removal.

    Args:
        obj: Object to get values from.

    Returns:
        ValuesView without "data" key.
    """
    cdef dict result = dict_mixin_get_vars_without_data(obj)
    return result.values()


cpdef object dict_mixin_items_fast(object obj):
    """
    Fast items() operation with "data" key removal.

    Args:
        obj: Object to get items from.

    Returns:
        ItemsView without "data" key.
    """
    cdef dict result = dict_mixin_get_vars_without_data(obj)
    return result.items()
