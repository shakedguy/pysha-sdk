# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
"""
Cython implementation of performance-critical crypto operations.

This module contains optimized Cython implementations for hot paths
in cryptographic operations.
"""

cimport cython
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy, strlen
import os
import time
import hashlib
from uuid import UUID
from datetime import UTC, datetime

from libc.stdint cimport uint64_t, uint8_t, uint32_t
from cpython.bytes cimport PyBytes_AS_STRING
from cpython.object cimport PyObject

cdef extern from "Python.h":
    object PyBytes_FromStringAndSize(const char *s, Py_ssize_t size)


# Hex encoding lookup table
cdef const char* HEX_CHARS = b"0123456789abcdef"

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

cpdef str calculate_md5_hash_cython(str content):
    """
    Fast MD5 hash calculation using Cython with optimized hex encoding.

    Args:
        content: String to hash.

    Returns:
        MD5 hash as hexadecimal string.
    """
    cdef bytes content_bytes = content.encode('utf-8')

    # Calculate MD5
    cdef bytes hash_bytes = hashlib.md5(content_bytes).digest()
    cdef Py_ssize_t hash_len = len(hash_bytes)

    # Allocate hex string buffer (2 chars per byte)
    cdef bytes hex_obj = PyBytes_FromStringAndSize(NULL, hash_len * 2)
    if hex_obj is None:
        raise MemoryError()

    cdef const uint8_t* hash_ptr = <const uint8_t*>hash_bytes
    cdef char* hex_ptr = <char*>PyBytes_AS_STRING(hex_obj)
    _bytes_to_hex(hash_ptr, hex_ptr, hash_len)

    return hex_obj.decode('ascii')


cpdef str encrypt_password_cython(str password, str salt):
    """
    Fast password encryption using scrypt with optimized hex encoding.

    Args:
        password: Password to encrypt.
        salt: Salt to use.

    Returns:
        Encrypted password as hexadecimal string.
    """
    cdef bytes password_bytes = password.encode('utf-8')
    cdef bytes salt_bytes = salt.encode('utf-8')

    # Calculate scrypt
    cdef bytes hash_bytes = hashlib.scrypt(
        password_bytes,
        salt=salt_bytes,
        n=16384,
        r=8,
        p=1,
        dklen=32
    )

    cdef Py_ssize_t hash_len = len(hash_bytes)

    # Allocate hex string buffer
    cdef bytes hex_obj = PyBytes_FromStringAndSize(NULL, hash_len * 2)
    if hex_obj is None:
        raise MemoryError()

    cdef const uint8_t* hash_ptr = <const uint8_t*>hash_bytes
    cdef char* hex_ptr = <char*>PyBytes_AS_STRING(hex_obj)
    _bytes_to_hex(hash_ptr, hex_ptr, hash_len)

    return hex_obj.decode('ascii')


cpdef bint match_password_cython(str password, str hash_str):
    """
    Fast password matching using Cython with optimized string operations.

    Args:
        password: Password to check.
        hash_str: Hashed password to compare against.

    Returns:
        True if password matches, False otherwise.
    """
    cdef Py_ssize_t hash_len = len(hash_str)
    if hash_len < 64:
        return False

    # Direct string slicing (Cython optimizes this)
    cdef str salt = hash_str[64:]
    cdef str original_pass_hash = hash_str[:64]
    cdef str current_pass_hash = encrypt_password_cython(password, salt)

    # Fast comparison - Cython optimizes string equality
    return original_pass_hash == current_pass_hash


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

cpdef str to_stable_uuid_cython(list parts):
    """
    Fast stable UUID generation from parts with optimized MD5 and hex operations.

    Args:
        parts: List of string parts to combine.

    Returns:
        Stable UUID string.
    """
    if not parts:
        return ""

    # Join parts efficiently
    cdef str joined = "|".join(parts)
    cdef bytes joined_bytes = joined.encode('utf-8')

    # Calculate MD5
    cdef bytes hash_bytes = hashlib.md5(joined_bytes).digest()
    cdef Py_ssize_t hash_len = len(hash_bytes)

    # Convert to hex with lowercase
    cdef bytes hex_obj = PyBytes_FromStringAndSize(NULL, hash_len * 2)
    if hex_obj is None:
        raise MemoryError()

    cdef const uint8_t* hash_ptr = <const uint8_t*>hash_bytes
    cdef char* hex_ptr = <char*>PyBytes_AS_STRING(hex_obj)
    _bytes_to_hex(hash_ptr, hex_ptr, hash_len)

    # Convert hex string to UUID bytes
    cdef bytes uuid_bytes_obj = PyBytes_FromStringAndSize(NULL, 16)
    if uuid_bytes_obj is None:
        raise MemoryError()

    cdef const char* hex_cstr = <const char*>PyBytes_AS_STRING(hex_obj)
    cdef uint8_t* uuid_bytes_ptr = <uint8_t*>PyBytes_AS_STRING(uuid_bytes_obj)
    _hex_to_bytes(hex_cstr, uuid_bytes_ptr, 32)

    return str(UUID(bytes=uuid_bytes_obj)).upper()




cdef inline void _write_u48_be(uint8_t* out, uint64_t x) nogil:
    out[0] = <uint8_t>(x >> 40)
    out[1] = <uint8_t>(x >> 32)
    out[2] = <uint8_t>(x >> 24)
    out[3] = <uint8_t>(x >> 16)
    out[4] = <uint8_t>(x >> 8)
    out[5] = <uint8_t>(x)

cpdef str uuidv7_cython():

    cdef uint64_t ts_ms = <uint64_t>(time.time_ns() // 1_000_000)
    cdef bytes rnd = os.urandom(10)

    cdef bytes b = PyBytes_FromStringAndSize(NULL, 16)
    if b is None:
        raise MemoryError()
    cdef uint8_t* p = <uint8_t*>PyBytes_AS_STRING(b)
    cdef const uint8_t* r = <const uint8_t*>rnd  # Cython can take buffer pointer for bytes

    # 48-bit big-endian timestamp
    _write_u48_be(p, ts_ms)

    # Version 7 in high nibble of byte 6 (first byte after timestamp)
    p[6] = (r[0] & 0x0F) | 0x70

    # Variant RFC 4122 in two MSBs of byte 7
    p[7] = (r[1] & 0x3F) | 0x80

    # Remaining random bytes
    p[8]  = r[2]
    p[9]  = r[3]
    p[10] = r[4]
    p[11] = r[5]
    p[12] = r[6]
    p[13] = r[7]
    p[14] = r[8]
    p[15] = r[9]

    return str(UUID(bytes=b))


cdef inline uint64_t _parse_hex_u48(const char* hex_str) nogil:
    """Parse 12 hex characters (48 bits) to uint64_t."""
    cdef uint64_t result = 0
    cdef Py_ssize_t i = 0
    while i < 12:
        result = (result << 4) | _hex_char_to_nibble(hex_str[i])
        i += 1
    return result

cpdef object uuidv7_to_datetime_cython(str uuid):
    """
    Fast datetime extraction from UUIDv7 using Cython with optimized hex parsing.

    Args:
        uuid: UUIDv7 string (hex, with or without dashes).

    Returns:
        datetime object or None if invalid.
    """
    if not uuid:
        return None

    cdef str clean_hex = uuid.replace("-", "")

    if len(clean_hex) != 32:
        raise ValueError("Invalid UUID string length")

    # Convert to bytes for C-level access
    cdef bytes hex_bytes = clean_hex.encode('ascii')
    cdef const char* hex_cstr = <const char*>PyBytes_AS_STRING(hex_bytes)

    # Parse first 12 hex characters (48 bits) directly
    cdef uint64_t timestamp_ms = _parse_hex_u48(hex_cstr)

    return datetime.fromtimestamp(<double>timestamp_ms / 1000.0, tz=UTC)
