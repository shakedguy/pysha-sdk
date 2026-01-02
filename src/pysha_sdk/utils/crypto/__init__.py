"""Crypto utilities module for pysha-sdk."""

# Always import non-optimized functions from Python implementation
from ..strings import AnyStr, to_str
from ._py import (
    generate_random_id,
    generate_random_token,
    generate_unique_secure_token,
    hash_password,
)

# Try to import Cython implementations for performance-critical functions
try:
    from ._native import (
        calculate_md5_hash_cython as _calculate_md5_hash,
    )
    from ._native import (
        encrypt_password_cython as _encrypt_password,
    )
    from ._native import (
        match_password_cython as _match_password,
    )
    from ._native import (
        to_stable_uuid_cython as _to_stable_uuid_cython,
    )
    from ._native import (
        uuidv7_cython as uuidv7,
    )
    from ._native import (
        uuidv7_to_datetime_cython as uuidv7_to_datetime,
    )

    # Wrap Cython functions to match Python API
    def calculate_md5_hash(content: str) -> str:
        return _calculate_md5_hash(content)

    def encrypt_password(password: str, salt: str) -> str:
        return _encrypt_password(password, salt)

    def match_password(password: str, hash_str: str) -> bool:
        return _match_password(password, hash_str)

    def to_stable_uuid(*parts: AnyStr) -> str:
        if not parts:
            return ""
        str_parts = [to_str(part) for part in parts]
        return _to_stable_uuid_cython(str_parts)

except ImportError:
    from ._py import (
        calculate_md5_hash,
        encrypt_password,
        match_password,
        to_stable_uuid,
        uuidv7,
        uuidv7_to_datetime,
    )
