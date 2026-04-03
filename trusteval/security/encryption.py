# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Fernet encryption utilities for secure key and data storage.

Provides symmetric encryption via ``cryptography.fernet.Fernet``, with
optional password-based key derivation using PBKDF2-HMAC-SHA256.  The
master encryption key is persisted at ``~/.trusteval/master.key`` with
restrictive file permissions.
"""

from __future__ import annotations

import base64
import os
import stat
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from trusteval.utils.exceptions import TrustEvalError

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------

_TRUSTEVAL_DIR = Path.home() / ".trusteval"
_MASTER_KEY_PATH = _TRUSTEVAL_DIR / "master.key"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_dir(directory: Path) -> None:
    """Create *directory* if it does not exist, with 700 permissions.

    Args:
        directory: Path to the directory to ensure.
    """
    directory.mkdir(parents=True, exist_ok=True)
    try:
        directory.chmod(stat.S_IRWXU)
    except OSError:
        pass  # Windows may not support chmod fully


def _restrict_file(filepath: Path) -> None:
    """Set file permissions to owner-read/write only (600).

    Args:
        filepath: Path to the file to restrict.
    """
    try:
        filepath.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass  # Graceful degradation on Windows


# ---------------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------------


def generate_key() -> bytes:
    """Generate a new Fernet-compatible encryption key.

    Returns:
        A 32-byte URL-safe base64-encoded key suitable for ``Fernet``.
    """
    return Fernet.generate_key()


# ---------------------------------------------------------------------------
# Encrypt / Decrypt
# ---------------------------------------------------------------------------


def encrypt(data: str, key: bytes) -> bytes:
    """Encrypt a plaintext string using the given Fernet key.

    Args:
        data: The plaintext string to encrypt.
        key: A Fernet-compatible encryption key.

    Returns:
        The encrypted ciphertext as bytes.

    Raises:
        TrustEvalError: If encryption fails.
    """
    try:
        fernet = Fernet(key)
        return fernet.encrypt(data.encode("utf-8"))
    except Exception as exc:
        raise TrustEvalError(
            f"Encryption failed: {exc}",
            details={"error_type": type(exc).__name__},
        ) from exc


def decrypt(encrypted_data: bytes, key: bytes) -> str:
    """Decrypt ciphertext back to a plaintext string.

    Args:
        encrypted_data: The Fernet-encrypted ciphertext.
        key: The Fernet key that was used for encryption.

    Returns:
        The original plaintext string.

    Raises:
        TrustEvalError: If decryption fails (wrong key or corrupted data).
    """
    try:
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data).decode("utf-8")
    except InvalidToken as exc:
        raise TrustEvalError(
            "Decryption failed — invalid key or corrupted ciphertext.",
            details={"error_type": "InvalidToken"},
        ) from exc
    except Exception as exc:
        raise TrustEvalError(
            f"Decryption failed: {exc}",
            details={"error_type": type(exc).__name__},
        ) from exc


# ---------------------------------------------------------------------------
# Password-based key derivation
# ---------------------------------------------------------------------------


def derive_key_from_password(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    """Derive a Fernet key from a human-memorable password using PBKDF2.

    Args:
        password: The password to derive the key from.
        salt: Optional 16-byte salt.  If ``None``, a cryptographically
            random salt is generated.

    Returns:
        A ``(key, salt)`` tuple.  The *salt* must be stored alongside the
        encrypted data to allow re-derivation.
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480_000,
    )
    raw_key = kdf.derive(password.encode("utf-8"))
    fernet_key = base64.urlsafe_b64encode(raw_key)
    return fernet_key, salt


# ---------------------------------------------------------------------------
# Master key management
# ---------------------------------------------------------------------------


def load_or_create_master_key(path: Path | None = None) -> bytes:
    """Load the master encryption key from disk, creating one if absent.

    The key file is stored with restrictive permissions (owner-only).

    Args:
        path: Filesystem path for the master key.  Defaults to
            ``~/.trusteval/master.key``.

    Returns:
        The master Fernet key as bytes.

    Raises:
        TrustEvalError: If the key file exists but cannot be read.
    """
    key_path = path or _MASTER_KEY_PATH
    _ensure_dir(key_path.parent)

    if key_path.is_file():
        try:
            key = key_path.read_bytes().strip()
            # Validate that it is a usable Fernet key
            Fernet(key)
            return key
        except Exception as exc:
            raise TrustEvalError(
                f"Master key at {key_path} is invalid or unreadable: {exc}",
                details={"path": str(key_path)},
            ) from exc

    # Generate and persist a new master key
    key = generate_key()
    key_path.write_bytes(key)
    _restrict_file(key_path)
    return key
