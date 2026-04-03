# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Encrypted API-key management for LLM providers.

Keys are encrypted at rest using Fernet symmetric encryption and stored
in ``~/.trusteval/keys.enc``.  Environment variables (e.g.
``OPENAI_API_KEY``) are used as a fallback when a key has not been
explicitly stored.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

from trusteval.security.encryption import (
    decrypt,
    encrypt,
    load_or_create_master_key,
)
from trusteval.utils.exceptions import TrustEvalError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TRUSTEVAL_DIR = Path.home() / ".trusteval"
_KEYS_FILE = _TRUSTEVAL_DIR / "keys.enc"

# Environment-variable lookup table: provider name -> env var name
_ENV_MAP: Dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "cohere": "COHERE_API_KEY",
    "huggingface": "HUGGINGFACE_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "groq": "GROQ_API_KEY",
    "xai": "XAI_API_KEY",
    "azure": "AZURE_OPENAI_API_KEY",
    "aws": "AWS_ACCESS_KEY_ID",
}


class KeyManager:
    """Encrypted key vault for LLM provider API keys.

    Keys are stored in a single Fernet-encrypted JSON file at
    ``~/.trusteval/keys.enc``.  The master encryption key is managed
    automatically and persisted at ``~/.trusteval/master.key``.

    Args:
        keys_path: Override the default encrypted-keys file location.
        master_key_path: Override the default master-key file location.

    Example::

        km = KeyManager()
        km.store_key("openai", "sk-abc123...")
        api_key = km.get_key("openai")
        print(km.mask_key(api_key))  # "sk-a****...c123"
    """

    def __init__(
        self,
        keys_path: Path | str | None = None,
        master_key_path: Path | str | None = None,
    ) -> None:
        self._keys_path = Path(keys_path) if keys_path else _KEYS_FILE
        self._master_key_path = (
            Path(master_key_path) if master_key_path else None
        )
        self._master_key: bytes = load_or_create_master_key(
            self._master_key_path
        )
        self._keys_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_keys(self) -> Dict[str, str]:
        """Load and decrypt the key store from disk.

        Returns:
            A dict mapping provider names to plaintext API keys.
        """
        if not self._keys_path.is_file():
            return {}
        try:
            encrypted_blob = self._keys_path.read_bytes()
            plaintext = decrypt(encrypted_blob, self._master_key)
            return json.loads(plaintext)
        except TrustEvalError:
            raise
        except Exception as exc:
            raise TrustEvalError(
                f"Failed to load key store: {exc}",
                details={"path": str(self._keys_path)},
            ) from exc

    def _save_keys(self, keys: Dict[str, str]) -> None:
        """Encrypt and write the key store to disk.

        Args:
            keys: Provider-to-key mapping to persist.
        """
        plaintext = json.dumps(keys, sort_keys=True)
        encrypted_blob = encrypt(plaintext, self._master_key)
        self._keys_path.write_bytes(encrypted_blob)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def store_key(self, provider: str, api_key: str) -> None:
        """Store an API key for the given provider.

        If a key already exists for *provider*, it is overwritten.

        Args:
            provider: Provider name (e.g. ``"openai"``).
            api_key: The raw API key string.

        Raises:
            TrustEvalError: If the key store cannot be written.
        """
        provider = provider.lower().strip()
        if not provider:
            raise TrustEvalError("Provider name must not be empty.")
        if not api_key:
            raise TrustEvalError("API key must not be empty.")

        keys = self._load_keys()
        keys[provider] = api_key
        self._save_keys(keys)

    def get_key(self, provider: str) -> str:
        """Retrieve the decrypted API key for *provider*.

        Resolution order:

        1. Encrypted key store (``~/.trusteval/keys.enc``).
        2. Environment variable (e.g. ``OPENAI_API_KEY``).

        Args:
            provider: Provider name.

        Returns:
            The plaintext API key.

        Raises:
            TrustEvalError: If no key is found for the provider.
        """
        provider = provider.lower().strip()
        keys = self._load_keys()

        # 1. Check encrypted store
        if provider in keys:
            return keys[provider]

        # 2. Environment-variable fallback
        env_var = _ENV_MAP.get(provider)
        if env_var:
            env_value = os.environ.get(env_var)
            if env_value:
                return env_value

        # 3. Generic fallback: PROVIDER_API_KEY
        generic_var = f"{provider.upper()}_API_KEY"
        env_value = os.environ.get(generic_var)
        if env_value:
            return env_value

        raise TrustEvalError(
            f"No API key found for provider '{provider}'. "
            f"Store one with KeyManager.store_key() or set the "
            f"{env_var or generic_var} environment variable.",
            details={"provider": provider},
        )

    def delete_key(self, provider: str) -> None:
        """Remove the stored key for *provider*.

        Args:
            provider: Provider name.

        Raises:
            TrustEvalError: If no stored key exists for the provider.
        """
        provider = provider.lower().strip()
        keys = self._load_keys()
        if provider not in keys:
            raise TrustEvalError(
                f"No stored key for provider '{provider}'.",
                details={"provider": provider},
            )
        del keys[provider]
        self._save_keys(keys)

    def list_providers(self) -> List[str]:
        """List providers that have stored keys.

        Returns:
            Sorted list of provider names.  **Never** returns actual keys.
        """
        return sorted(self._load_keys().keys())

    def rotate_key(self, provider: str, new_key: str) -> None:
        """Replace an existing key with a new one.

        This is functionally equivalent to ``store_key`` but explicitly
        signals intent and validates that a previous key existed.

        Args:
            provider: Provider name.
            new_key: The replacement API key.

        Raises:
            TrustEvalError: If no previous key exists for the provider.
        """
        provider = provider.lower().strip()
        keys = self._load_keys()
        if provider not in keys:
            raise TrustEvalError(
                f"Cannot rotate — no existing key for provider '{provider}'.",
                details={"provider": provider},
            )
        if not new_key:
            raise TrustEvalError("New API key must not be empty.")
        keys[provider] = new_key
        self._save_keys(keys)

    @staticmethod
    def mask_key(api_key: str) -> str:
        """Return a masked representation of an API key.

        Preserves the first recognisable prefix and the last four
        characters, replacing the middle with asterisks.

        Args:
            api_key: The raw API key.

        Returns:
            A string like ``"sk-****...abcd"`` that is safe to log.

        Examples:
            >>> KeyManager.mask_key("sk-abc123456789xyz")
            'sk-****...9xyz'
            >>> KeyManager.mask_key("short")
            '****'
        """
        if not api_key or len(api_key) < 8:
            return "****"

        # Detect common prefixes (sk-, gsk_, hf_, xai-, key-)
        prefix = ""
        for p in ("sk-", "gsk_", "hf_", "xai-", "key-"):
            if api_key.startswith(p):
                prefix = p
                break

        suffix = api_key[-4:]
        return f"{prefix}****...{suffix}"
