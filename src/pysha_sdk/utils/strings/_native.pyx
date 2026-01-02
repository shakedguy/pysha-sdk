# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
"""
Cython implementation of performance-critical string operations.

This module contains optimized Cython implementations for hot paths
in string manipulation operations using C-level memory operations.
"""

cimport cython
from libc.stdint cimport uint8_t, uint64_t
from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AS_STRING
from cpython.unicode cimport PyUnicode_Check

cdef extern from "Python.h":
    object PyBytes_FromStringAndSize(const char *s, Py_ssize_t size)
    int PyUnicode_READY(object o)
    Py_ssize_t PyUnicode_GET_LENGTH(object o)
    int PyUnicode_KIND(object o)
    void* PyUnicode_DATA(object o)

# Hex encoding lookup table (reused from crypto)
cdef const char* HEX_CHARS = b"0123456789abcdef"

# Hebrew character range: U+0590 to U+05FF
cdef inline bint _is_hebrew_char(int char_code) nogil:
    """Check if character code is in Hebrew range."""
    return char_code >= 0x0590 and char_code <= 0x05FF

cdef inline bint _is_hex_char(char c) nogil:
    """Check if character is valid hex digit."""
    cdef char c0 = 48  # '0'
    cdef char c9 = 57  # '9'
    cdef char ca = 97  # 'a'
    cdef char cf = 102  # 'f'
    cdef char cA = 65  # 'A'
    cdef char cF = 70  # 'F'
    return (c >= c0 and c <= c9) or (c >= ca and c <= cf) or (c >= cA and c <= cF)

cdef inline bint _is_digit_char(char c) nogil:
    """Check if character is a digit."""
    return c >= 48 and c <= 57  # '0' to '9'

cdef inline void _bytes_to_hex(const uint8_t* data, char* out, Py_ssize_t length) nogil:
    """Convert bytes to hex string using lookup table."""
    cdef Py_ssize_t i
    cdef uint8_t byte_val
    i = 0
    while i < length:
        byte_val = data[i]
        out[i * 2] = HEX_CHARS[byte_val >> 4]
        out[i * 2 + 1] = HEX_CHARS[byte_val & 0x0F]
        i += 1

cdef inline uint8_t _hex_char_to_nibble(char c) nogil:
    """Convert hex character to 4-bit value."""
    cdef char c0 = 48  # '0'
    cdef char c9 = 57  # '9'
    cdef char ca = 97  # 'a'
    cdef char cf = 102  # 'f'
    cdef char cA = 65  # 'A'
    cdef char cF = 70  # 'F'

    if c >= c0 and c <= c9:
        return <uint8_t>(c - c0)
    elif c >= ca and c <= cf:
        return <uint8_t>(c - ca + 10)
    elif c >= cA and c <= cF:
        return <uint8_t>(c - cA + 10)
    return 0

cdef inline void _hex_to_bytes(const char* hex_str, uint8_t* out, Py_ssize_t hex_len) nogil:
    """Convert hex string to bytes."""
    cdef Py_ssize_t i, byte_count
    byte_count = hex_len // 2
    i = 0
    while i < byte_count:
        out[i] = (_hex_char_to_nibble(hex_str[i * 2]) << 4) | _hex_char_to_nibble(hex_str[i * 2 + 1])
        i += 1

cpdef bint is_ascii_cython(str text):
    """
    Fast ASCII check using Cython with direct character code access.

    Args:
        text: String to check.

    Returns:
        True if all characters are ASCII, False otherwise.
    """
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t length = len(text)
    cdef int char_code

    while i < length:
        char_code = ord(text[i])
        if char_code >= 128:
            return False
        i += 1
    return True


cpdef str extract_digits_cython(str text):
    """
    Fast digit extraction using Cython with pre-allocated buffer.

    Args:
        text: String to extract digits from.

    Returns:
        String containing only digits.
    """
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t length = len(text)
    cdef Py_ssize_t digit_count = 0
    cdef str char
    cdef list digits = []

    # First pass: count digits to estimate size
    while i < length:
        char = text[i]
        if char.isdigit():
            digits.append(char)
        i += 1

    return ''.join(digits)


cpdef str to_upper_first_cython(str text):
    """
    Fast first character uppercase conversion with direct memory access.

    Args:
        text: String to convert.

    Returns:
        String with first character uppercased.
    """
    cdef Py_ssize_t length = len(text)

    if length == 0:
        return text
    elif length == 1:
        return text.upper()
    else:
        return text[0].upper() + text[1:]


cpdef bint is_valid_israeli_id_cython(str text):
    """
    Fast Israeli ID validation using Cython with optimized checksum calculation.

    Args:
        text: ID string to validate.

    Returns:
        True if valid Israeli ID, False otherwise.
    """
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t length = len(text)
    cdef int digit
    cdef int step
    cdef int total = 0
    cdef str char
    cdef str padded_text

    if length > 9:
        return False

    # Check if all characters are digits
    while i < length:
        char = text[i]
        if not char.isdigit():
            return False
        i += 1

    # Pad with zeros to 9 digits
    padded_text = text.zfill(9)

    # Calculate checksum with optimized loop
    i = 0
    while i < 9:
        digit = int(padded_text[i])
        step = digit * ((i % 2) + 1)
        total += step - 9 if step > 9 else step
        i += 1

    return (total % 10) == 0


cpdef bint is_hex_cython(str text):
    """
    Fast hex string validation using Cython with direct character checking.

    Args:
        text: String to check.

    Returns:
        True if string is valid hex, False otherwise.
    """
    if not text:
        return False

    cdef bytes text_bytes = text.encode('ascii')
    cdef const char* text_ptr = <const char*>text_bytes
    cdef Py_ssize_t length = len(text_bytes)
    cdef Py_ssize_t i = 0

    while i < length:
        if not _is_hex_char(text_ptr[i]):
            return False
        i += 1

    return True


cpdef bint is_hebrew_cython(str text):
    """
    Fast Hebrew character detection using Cython with direct character code checking.

    Args:
        text: String to check.

    Returns:
        True if text contains Hebrew characters, False otherwise.
    """
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t length = len(text)
    cdef int char_code

    while i < length:
        char_code = ord(text[i])
        if _is_hebrew_char(char_code):
            return True
        i += 1

    return False


cpdef str to_hex_cython(str text):
    """
    Fast hex encoding using Cython with direct memory operations.

    Args:
        text: String to encode.

    Returns:
        Hex-encoded string.
    """
    cdef bytes text_bytes = text.encode('utf-8')
    cdef Py_ssize_t text_len = len(text_bytes)

    # Allocate hex string buffer (2 chars per byte)
    cdef bytes hex_obj = PyBytes_FromStringAndSize(NULL, text_len * 2)
    if hex_obj is None:
        raise MemoryError()

    cdef const uint8_t* text_ptr = <const uint8_t*>text_bytes
    cdef char* hex_ptr = <char*>PyBytes_AS_STRING(hex_obj)
    _bytes_to_hex(text_ptr, hex_ptr, text_len)

    return hex_obj.decode('ascii')


cpdef str from_hex_cython(str text):
    """
    Fast hex decoding using Cython with direct memory operations.

    Args:
        text: Hex string to decode.

    Returns:
        Decoded string.
    """
    cdef bytes hex_bytes = text.encode('ascii')
    cdef Py_ssize_t hex_len = len(hex_bytes)

    if hex_len % 2 != 0:
        raise ValueError("Hex string must have even length")

    # Allocate output buffer
    cdef Py_ssize_t byte_count = hex_len // 2
    cdef bytes output = PyBytes_FromStringAndSize(NULL, byte_count)
    if output is None:
        raise MemoryError()

    cdef const char* hex_ptr = <const char*>hex_bytes
    cdef uint8_t* out_ptr = <uint8_t*>PyBytes_AS_STRING(output)
    _hex_to_bytes(hex_ptr, out_ptr, hex_len)

    return output.decode('utf-8')


cpdef str to_base64_cython(str text):
    """
    Fast base64 encoding using Cython with optimized memory operations.

    Args:
        text: String to encode.

    Returns:
        Base64-encoded string.
    """
    import base64
    cdef bytes text_bytes = text.encode('utf-8')
    cdef bytes encoded = base64.b64encode(text_bytes)
    return encoded.decode('ascii')


cpdef str from_base64_cython(str text):
    """
    Fast base64 decoding using Cython with optimized memory operations.

    Args:
        text: Base64 string to decode.

    Returns:
        Decoded string.
    """
    import base64
    cdef bytes text_bytes = text.encode('ascii')
    cdef bytes decoded = base64.b64decode(text_bytes)
    return decoded.decode('utf-8')


cpdef str to_ascii_cython(str text):
    """
    Fast ASCII conversion using Cython with direct character filtering.

    Args:
        text: String to convert.

    Returns:
        ASCII-only string.
    """
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t length = len(text)
    cdef list ascii_chars = []
    cdef int char_code
    cdef str char

    while i < length:
        char = text[i]
        char_code = ord(char)
        if char_code < 128:
            ascii_chars.append(char)
        i += 1

    return ''.join(ascii_chars)
