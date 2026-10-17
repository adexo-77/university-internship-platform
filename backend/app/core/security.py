"""Security helpers for password hashing and session token management."""

import hashlib
import hmac
import secrets

# Scrypt hashing parameters as named constants
SCRYPT_N: int = 16384
SCRYPT_R: int = 8
SCRYPT_P: int = 1
SCRYPT_DKLEN: int = 64
SCRYPT_SALT_BYTES: int = 16

# Session token and cookie parameters as named constants
SESSION_TOKEN_BYTES: int = 32
SESSION_COOKIE_NAME: str = "session_token"
SESSION_LIFETIME_DAYS: int = 7
SESSION_LIFETIME_SECONDS: int = SESSION_LIFETIME_DAYS * 24 * 60 * 60


def hash_password(password: str) -> str:
    """Hash a password using hashlib.scrypt with a cryptographically secure random salt."""
    salt = secrets.token_bytes(SCRYPT_SALT_BYTES)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )
    return f"{salt.hex()}${derived.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify a plain password against a stored scrypt hash using constant-time comparison.

    Safe against malformed, corrupted, or non-hex stored hashes.
    """
    try:
        if not stored_hash or "$" not in stored_hash:
            return False
        parts = stored_hash.split("$")
        if len(parts) != 2:
            return False
        salt = bytes.fromhex(parts[0])
        expected_key = bytes.fromhex(parts[1])
        if len(salt) != SCRYPT_SALT_BYTES or len(expected_key) != SCRYPT_DKLEN:
            return False
        computed_key = hashlib.scrypt(
            plain_password.encode("utf-8"),
            salt=salt,
            n=SCRYPT_N,
            r=SCRYPT_R,
            p=SCRYPT_P,
            dklen=SCRYPT_DKLEN,
        )
        return hmac.compare_digest(computed_key, expected_key)
    except Exception:
        return False


# Pre-computed dummy hash to run verification against for non-existent users,
# preventing timing attacks from leaking whether an email exists.
DUMMY_PASSWORD_HASH: str = hash_password("dummy-password-for-timing-defense")


def verify_dummy_password(plain_password: str) -> bool:
    """Execute scrypt calculation on dummy hash for identical timing on unknown users."""
    return verify_password(plain_password, DUMMY_PASSWORD_HASH)


def generate_session_token() -> str:
    """Generate a high-entropy URL-safe session token."""
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    """Compute SHA-256 hash of a session token for secure database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
