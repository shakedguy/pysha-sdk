# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
"""
Cython implementation of performance-critical object operations.

This module contains optimized Cython implementations for hot paths
in object manipulation operations using C-level optimizations.
"""

cimport cython
from cpython.dict cimport PyDict_Check
from cpython.list cimport PyList_Check
from cpython.tuple cimport PyTuple_Check
from cpython.set cimport PySet_Check
from cpython.unicode cimport PyUnicode_Check
from cpython.bytes cimport PyBytes_Check
from cpython.bytearray cimport PyByteArray_Check
from cpython.memoryview cimport PyMemoryView_Check
from cpython.sequence cimport PySequence_Fast, PySequence_Fast_GET_SIZE, PySequence_Fast_GET_ITEM

cpdef object change_keys_case(object input_obj, object method, bint deep=True):
    """
    Fast key case conversion using Cython with C-level type checking.

    Args:
        input_obj: Object to convert (dict, list, tuple, set, or string-like).
        method: Function to apply to keys/strings.
        deep: Whether to apply conversion recursively.

    Returns:
        Object with keys converted using the specified method.
    """

    cdef dict d
    cdef dict out
    cdef object k, key, value, new_key, new_k
    cdef object seq_fast
    cdef Py_ssize_t n, i
    cdef list tmp
    cdef object item

    # String-like: just apply method and return
    if PyUnicode_Check(input_obj) or PyBytes_Check(input_obj) or PyByteArray_Check(input_obj) or PyMemoryView_Check(input_obj):
        return method(input_obj)

    # Dictionary handling
    if PyDict_Check(input_obj):
        d = <dict>input_obj

        # Leading "_" merge logic (mutates input dict)
        for k in list(d.keys()):
            if isinstance(k, str) and k.startswith("_"):
                new_k = (<str>k).lstrip("_")
                if new_k in d:
                    d[new_k] = d[new_k] or d[k]

        out = {}
        for key, value in d.items():
            # Ensure key is str for method
            if not isinstance(key, str):
                key = str(key)
            new_key = method(key)
            if deep and is_iterable_except_str_like_cython(value):
                out[new_key] = change_keys_case(value, method, deep)
            else:
                out[new_key] = value
        return out

    # List/tuple/set handling
    if PyList_Check(input_obj) or PyTuple_Check(input_obj) or PySet_Check(input_obj):
        seq_fast = PySequence_Fast(input_obj, "expected iterable")
        if seq_fast is None:
            raise ValueError("Invalid input, must be an iterable")

        n = PySequence_Fast_GET_SIZE(seq_fast)
        tmp = []
        i = 0
        while i < n:
            item = <object>PySequence_Fast_GET_ITEM(seq_fast, i)
            if deep and is_iterable_except_str_like_cython(item):
                tmp.append(change_keys_case(item, method, deep))
            else:
                tmp.append(item)
            i += 1

        if PySet_Check(input_obj):
            return set(tmp)
        elif PyTuple_Check(input_obj):
            return tuple(tmp)
        else:
            return tmp

    return input_obj


cpdef bint is_iterable_except_str_like_cython(object obj):
    """
    Fast iterable check excluding string-like objects using Cython.

    Args:
        obj: Object to check.

    Returns:
        True if object is iterable but not string-like, False otherwise.
    """
    # Fast path for common string-like types (Cython optimizes isinstance)
    if isinstance(obj, (str, bytes, bytearray, memoryview)):
        return False

    # Fast path for common iterable types
    if isinstance(obj, (dict, list, tuple, set)):
        return True

    # Fallback to try/except for other types
    try:
        iter(obj)
        return True
    except TypeError:
        return False


cpdef dict recursive_sort_keys_cython(dict input_dict):
    """
    Fast recursive key sorting for dictionaries using Cython.

    Args:
        input_dict: Dictionary to sort.

    Returns:
        Dictionary with sorted keys recursively.
    """
    cdef dict result = {}
    cdef list sorted_items
    cdef list new_list
    cdef object key, value, item

    # Sort items (Cython optimizes sorted() for dict.items())
    sorted_items = sorted(input_dict.items())

    # Build result with recursive sorting
    for key, value in sorted_items:
        if isinstance(value, dict):
            result[key] = recursive_sort_keys_cython(value)
        elif isinstance(value, (list, tuple)):
            # Optimized list comprehension
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(recursive_sort_keys_cython(item))
                else:
                    new_list.append(item)
            result[key] = new_list
        else:
            result[key] = value

    return result
