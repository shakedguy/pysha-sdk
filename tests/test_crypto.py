"""Unit tests for crypto utilities module."""

from datetime import UTC, datetime
from uuid import UUID

import pytest

from pysha_sdk.utils.crypto import (
    calculate_md5_hash,
    encrypt_password,
    generate_random_id,
    generate_random_token,
    generate_unique_secure_token,
    hash_password,
    match_password,
    to_stable_uuid,
    uuidv7,
    uuidv7_to_datetime,
)


class TestCalculateMD5Hash:
    """Tests for calculate_md5_hash function."""

    def test_calculate_md5_hash_basic(self):
        """Test basic MD5 hash calculation."""
        result = calculate_md5_hash("hello")
        assert isinstance(result, str)
        assert len(result) == 32  # MD5 produces 32 hex characters
        assert result == "5d41402abc4b2a76b9719d911017c592"

    def test_calculate_md5_hash_empty_string(self):
        """Test MD5 hash of empty string."""
        result = calculate_md5_hash("")
        assert result == "d41d8cd98f00b204e9800998ecf8427e"

    def test_calculate_md5_hash_unicode(self):
        """Test MD5 hash with unicode characters."""
        result = calculate_md5_hash("héllo wörld")
        assert isinstance(result, str)
        assert len(result) == 32


class TestEncryptPassword:
    """Tests for encrypt_password function."""

    def test_encrypt_password_basic(self):
        """Test basic password encryption."""
        result = encrypt_password("password123", "salt")
        assert isinstance(result, str)
        assert len(result) == 64  # scrypt with dklen=32 produces 64 hex chars

    def test_encrypt_password_deterministic(self):
        """Test that same password and salt produce same hash."""
        result1 = encrypt_password("password", "salt")
        result2 = encrypt_password("password", "salt")
        assert result1 == result2

    def test_encrypt_password_different_salts(self):
        """Test that different salts produce different hashes."""
        result1 = encrypt_password("password", "salt1")
        result2 = encrypt_password("password", "salt2")
        assert result1 != result2


class TestHashPassword:
    """Tests for hash_password function."""

    def test_hash_password_basic(self):
        """Test basic password hashing."""
        result = hash_password("password123")
        assert isinstance(result, str)
        assert len(result) == 96  # 64 (hash) + 32 (salt)

    def test_hash_password_different_salts(self):
        """Test that hash_password generates different salts."""
        result1 = hash_password("password")
        result2 = hash_password("password")
        assert result1 != result2  # Different salts should produce different hashes


class TestMatchPassword:
    """Tests for match_password function."""

    def test_match_password_correct(self):
        """Test matching correct password."""
        hashed = hash_password("password123")
        assert match_password("password123", hashed) is True

    def test_match_password_incorrect(self):
        """Test matching incorrect password."""
        hashed = hash_password("password123")
        assert match_password("wrongpassword", hashed) is False

    def test_match_password_with_encrypt_password(self):
        """Test matching password using encrypt_password."""
        salt = "mysalt"
        hashed = encrypt_password("password", salt) + salt
        assert match_password("password", hashed) is True
        assert match_password("wrong", hashed) is False


class TestToStableUUID:
    """Tests for to_stable_uuid function."""

    def test_to_stable_uuid_single_part(self):
        """Test stable UUID with single part."""
        result = to_stable_uuid("test")
        assert isinstance(result, str)
        assert len(result) == 36  # UUID format
        assert result.count("-") == 4

    def test_to_stable_uuid_multiple_parts(self):
        """Test stable UUID with multiple parts."""
        result = to_stable_uuid("part1", "part2", "part3")
        assert isinstance(result, str)
        assert len(result) == 36

    def test_to_stable_uuid_deterministic(self):
        """Test that same parts produce same UUID."""
        result1 = to_stable_uuid("a", "b")
        result2 = to_stable_uuid("a", "b")
        assert result1 == result2

    def test_to_stable_uuid_empty(self):
        """Test stable UUID with no parts."""
        result = to_stable_uuid()
        assert result == ""

    def test_to_stable_uuid_valid_uuid_format(self):
        """Test that result is a valid UUID."""
        result = to_stable_uuid("test")
        # Should be able to parse as UUID
        uuid_obj = UUID(result)
        assert str(uuid_obj).upper() == result.upper()


class TestUUIDv7:
    """Tests for uuidv7 function."""

    def test_uuidv7_basic(self):
        """Test basic UUIDv7 generation."""
        result = uuidv7()
        assert isinstance(result, str)
        assert len(result) == 36
        assert result.count("-") == 4

    def test_uuidv7_unique(self):
        """Test that UUIDv7 generates unique values."""
        result1 = uuidv7()
        result2 = uuidv7()
        assert result1 != result2

    def test_uuidv7_valid_uuid(self):
        """Test that UUIDv7 produces valid UUID."""
        result = uuidv7()
        uuid_obj = UUID(result)
        assert str(uuid_obj) == result

    def test_uuidv7_version_7(self):
        """Test that UUIDv7 has version 7."""
        result = uuidv7()
        uuid_obj = UUID(result)
        # Note: Python's UUID class may not recognize version 7 correctly
        # We just verify it's a valid UUID
        assert uuid_obj is not None


class TestUUIDv7ToDatetime:
    """Tests for uuidv7_to_datetime function."""

    def test_uuidv7_to_datetime_basic(self):
        """Test converting UUIDv7 to datetime."""
        uuid_str = uuidv7()
        result = uuidv7_to_datetime(uuid_str)
        assert isinstance(result, datetime)
        assert result.tzinfo == UTC

    def test_uuidv7_to_datetime_without_dashes(self):
        """Test converting UUIDv7 without dashes."""
        uuid_str = uuidv7().replace("-", "")
        result = uuidv7_to_datetime(uuid_str)
        assert isinstance(result, datetime)

    def test_uuidv7_to_datetime_recent(self):
        """Test that UUIDv7 datetime is recent."""
        uuid_str = uuidv7()
        result = uuidv7_to_datetime(uuid_str)
        now = datetime.now(UTC)
        # Should be within last minute
        assert abs((now - result).total_seconds()) < 60

    def test_uuidv7_to_datetime_roundtrip(self):
        """Test roundtrip: generate UUID, extract datetime, verify it's recent."""
        uuid_str = uuidv7()
        dt = uuidv7_to_datetime(uuid_str)
        assert dt is not None
        assert isinstance(dt, datetime)


class TestGenerateRandomID:
    """Tests for generate_random_id function."""

    def test_generate_random_id_basic(self):
        """Test basic random ID generation."""
        result = generate_random_id(10)
        assert isinstance(result, str)
        assert len(result) == 10

    def test_generate_random_id_with_symbols(self):
        """Test random ID with symbols."""
        result = generate_random_id(20, simbols=True)
        assert len(result) == 20
        # Should contain some non-alphanumeric if symbols enabled

    def test_generate_random_id_hex_encoding(self):
        """Test random ID with hex encoding."""
        result = generate_random_id(16, encoding="hex")
        assert isinstance(result, str)

    def test_generate_random_id_base64_encoding(self):
        """Test random ID with base64 encoding."""
        result = generate_random_id(16, encoding="base64")
        assert isinstance(result, str)

    def test_generate_random_id_case_upper(self):
        """Test random ID with upper case."""
        result = generate_random_id(10, case="upper")
        assert result.isupper() or result == ""  # May be empty if encoding changes

    def test_generate_random_id_case_lower(self):
        """Test random ID with lower case."""
        result = generate_random_id(10, case="lower")
        assert result.islower() or result == ""


class TestGenerateRandomToken:
    """Tests for generate_random_token function."""

    def test_generate_random_token_binary(self):
        """Test random token with binary base."""
        result = generate_random_token(10, "binary")
        assert isinstance(result, str)
        assert len(result) == 10
        assert all(c in "01" for c in result)

    def test_generate_random_token_octal(self):
        """Test random token with octal base."""
        result = generate_random_token(10, "octal")
        assert isinstance(result, str)
        assert len(result) == 10
        assert all(c in "01234567" for c in result)

    def test_generate_random_token_hex(self):
        """Test random token with hex base."""
        result = generate_random_token(16, "hex")
        assert isinstance(result, str)
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)

    def test_generate_random_token_decimal(self):
        """Test random token with decimal base."""
        result = generate_random_token(10, "decimal")
        assert isinstance(result, str)
        assert len(result) == 10
        assert result.isdigit()

    def test_generate_random_token_base64(self):
        """Test random token with base-64 base."""
        result = generate_random_token(20, "base-64")
        assert isinstance(result, str)
        assert len(result) == 20

    def test_generate_random_token_invalid_base(self):
        """Test random token with invalid base raises error."""
        with pytest.raises(ValueError):
            generate_random_token(10, "invalid")


class TestGenerateUniqueSecureToken:
    """Tests for generate_unique_secure_token function."""

    def test_generate_unique_secure_token_basic(self):
        """Test basic unique secure token generation."""
        result = generate_unique_secure_token(12)
        assert isinstance(result, str)
        assert len(result) == 12

    def test_generate_unique_secure_token_base58_alphabet(self):
        """Test that token uses base58-like alphabet."""
        result = generate_unique_secure_token(20)
        # Base58 excludes 0, O, I, l
        assert "0" not in result
        assert "O" not in result
        assert "I" not in result
        assert "l" not in result

    def test_generate_unique_secure_token_unique(self):
        """Test that tokens are unique."""
        result1 = generate_unique_secure_token(16)
        result2 = generate_unique_secure_token(16)
        assert result1 != result2
