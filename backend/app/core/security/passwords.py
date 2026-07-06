"""Password hashing using Argon2id.

Isolated here so the algorithm can change without touching auth logic. Argon2id
is the current OWASP-recommended password hash and has no bcrypt-style length
truncation.
"""

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _hasher.verify(hashed_password, plain_password)
    except Argon2Error:
        return False
