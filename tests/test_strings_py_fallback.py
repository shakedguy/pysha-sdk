"""Unit tests for string utilities Python fallback implementations."""


# Test the Python fallback implementations directly
from pysha_sdk.utils.strings._py import (
    extract_digits as extract_digits_py,
)
from pysha_sdk.utils.strings._py import (
    from_base64 as from_base64_py,
)
from pysha_sdk.utils.strings._py import (
    from_hex as from_hex_py,
)
from pysha_sdk.utils.strings._py import (
    is_ascii as is_ascii_py,
)
from pysha_sdk.utils.strings._py import (
    is_hebrew as is_hebrew_py,
)
from pysha_sdk.utils.strings._py import (
    is_hex as is_hex_py,
)
from pysha_sdk.utils.strings._py import (
    is_valid_israeli_id as is_valid_israeli_id_py,
)
from pysha_sdk.utils.strings._py import (
    to_ascii as to_ascii_py,
)
from pysha_sdk.utils.strings._py import (
    to_base64 as to_base64_py,
)
from pysha_sdk.utils.strings._py import (
    to_hex as to_hex_py,
)
from pysha_sdk.utils.strings._py import (
    to_upper_first as to_upper_first_py,
)


class TestPythonFallback:
    """Tests for Python fallback implementations."""

    def test_extract_digits_py(self):
        """Test Python fallback extract_digits."""
        assert extract_digits_py("abc123") == "123"

    def test_is_ascii_py(self):
        """Test Python fallback is_ascii."""
        assert is_ascii_py("hello") is True
        assert is_ascii_py("héllo") is False

    def test_is_valid_israeli_id_py(self):
        """Test Python fallback is_valid_israeli_id."""
        assert is_valid_israeli_id_py("123456782") is True

    def test_to_upper_first_py(self):
        """Test Python fallback to_upper_first."""
        assert to_upper_first_py("hello") == "Hello"

    def test_is_hex_py(self):
        """Test Python fallback is_hex."""
        assert is_hex_py("deadbeef") is True
        assert is_hex_py("nothex") is False

    def test_is_hebrew_py(self):
        """Test Python fallback is_hebrew."""
        assert is_hebrew_py("שלום") is True
        assert is_hebrew_py("hello") is False

    def test_to_hex_py(self):
        """Test Python fallback to_hex."""
        result = to_hex_py("hello")
        assert isinstance(result, str)
        assert len(result) == 10  # 5 chars * 2

    def test_from_hex_py(self):
        """Test Python fallback from_hex."""
        result = from_hex_py("68656c6c6f")
        assert result == "hello"

    def test_to_base64_py(self):
        """Test Python fallback to_base64."""
        result = to_base64_py("hello")
        assert isinstance(result, str)

    def test_from_base64_py(self):
        """Test Python fallback from_base64."""
        result = from_base64_py("aGVsbG8=")
        assert result == "hello"

    def test_to_ascii_py(self):
        """Test Python fallback to_ascii."""
        result = to_ascii_py("héllo")
        assert isinstance(result, str)
        assert "é" not in result
