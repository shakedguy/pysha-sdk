"""Pure Python fallback implementations for string utilities."""

import base64
from typing import Union

from .regex import RE_DIGITS, RE_HEBREW, RE_HEX

AnyStr = Union[bytes, str, bytearray, memoryview]


def to_str(text: AnyStr) -> str:
    """Convert input to string."""
    if not isinstance(text, (str, bytes, bytearray, memoryview)):
        raise ValueError(
            "Input must be a string, bytes, bytearray, or memoryview"
        )
    return str(text) if isinstance(text, str) else text.decode()


def extract_digits(text: AnyStr) -> str:
    """
    Extracts all digits from the input string.

    Args:
        text (AnyStr): The input string to extract digits from.

    Returns:
        str: The extracted digits.
    """
    text = to_str(text)
    return "".join(RE_DIGITS.findall(text))


def is_ascii(text: AnyStr) -> bool:
    """
    Checks if the given string is ASCII.

    Args:
        text (AnyStr): The string to check.

    Returns:
        bool: True if the string is ASCII, False otherwise.
    """
    text = to_str(text)
    return all(ord(char) < 128 for char in text)


def is_valid_israeli_id(text: AnyStr) -> bool:
    """
    Validates an Israeli ID number using the Luhn algorithm variant.

    Args:
        text (AnyStr): The ID string to validate.

    Returns:
        bool: True if valid Israeli ID, False otherwise.
    """
    text = to_str(text)
    if len(text) > 9 or not text.isdigit():
        return False
    text = text.zfill(9)
    total = 0
    for i, digit_char in enumerate(text):
        digit = int(digit_char)
        step = digit * ((i % 2) + 1)
        total += step - 9 if step > 9 else step
    return total % 10 == 0


def to_upper_first(text: AnyStr) -> str:
    """
    Converts the first character of a string to uppercase.

    Args:
        text (AnyStr): The input text to convert.

    Returns:
        str: The converted string with the first character in uppercase.
    """
    text = to_str(text)
    return text[:1].upper() + text[1:] if len(text) > 1 else text.upper()


def is_hex(text: AnyStr) -> bool:
    """
    Checks if the given string is a valid hexadecimal string.

    Args:
        text (AnyStr): The string to check.

    Returns:
        bool: True if the string is a valid hexadecimal string, False otherwise.
    """
    text = to_str(text)
    return bool(RE_HEX.fullmatch(text))


def is_hebrew(text: AnyStr) -> bool:
    """
    Check if the text contains Hebrew characters.

    Args:
        text (AnyStr): The input text to check.

    Returns:
        bool: True if the text contains Hebrew characters, False otherwise.
    """
    text = to_str(text)
    return bool(RE_HEBREW.search(text))


def to_hex(text: AnyStr) -> str:
    """
    Converts a string to its hexadecimal representation.

    Args:
        text (AnyStr): The input text to convert.

    Returns:
        str: The hexadecimal encoded string.
    """
    text = to_str(text)
    return text if is_hex(text) else text.encode().hex()


def from_hex(text: AnyStr) -> str:
    """
    Converts a hexadecimal encoded string back to its original representation.

    Args:
        text (AnyStr): The hexadecimal encoded text to convert.

    Returns:
        str: The decoded string.
    """
    text = to_str(text)
    return bytes.fromhex(text).decode()


def to_base64(text: AnyStr) -> str:
    """
    Converts a string to its Base64 representation.

    Args:
        text (AnyStr): The input text to convert.

    Returns:
        str: The Base64 encoded string.
    """
    text = to_str(text)
    # Check if already base64
    try:
        if base64.b64decode(text, validate=True):
            return text
    except Exception:
        pass
    return base64.b64encode(text.encode()).decode()


def from_base64(text: AnyStr) -> str:
    """
    Converts a Base64 encoded string back to its original representation.

    Args:
        text (AnyStr): The Base64 encoded text to convert.

    Returns:
        str: The decoded string.
    """
    text = to_str(text)
    # Check if base64
    try:
        if base64.b64decode(text, validate=True):
            return base64.b64decode(text).decode()
    except Exception:
        pass
    return text


def to_ascii(text: AnyStr) -> str:
    """
    Converts a string to its ASCII representation.

    Args:
        text (AnyStr): The input text to convert.

    Returns:
        str: The ASCII encoded string.
    """
    text = to_str(text)
    return text.encode("ascii", "ignore").decode()
