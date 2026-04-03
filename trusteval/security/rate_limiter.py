# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Token-bucket rate limiter for LLM provider API calls.

Enforces per-provider request rate limits using a token-bucket algorithm.
Buckets refill continuously and are configurable per provider or via a
global default.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Internal bucket representation
# ---------------------------------------------------------------------------


@dataclass
class _Bucket:
    """State for a single token bucket.

    Attributes:
        capacity: Maximum number of tokens the bucket can hold.
        tokens: Current number of available tokens.
        refill_rate: Tokens added per second.
        last_refill: Timestamp of the most recent refill calculation.
    """

    capacity: float
    tokens: float
    refill_rate: float
    last_refill: float = field(default_factory=time.monotonic)

    def refill(self) -> None:
        """Add tokens that have accumulated since the last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class RateLimiter:
    """Per-provider token-bucket rate limiter.

    Each provider gets its own bucket.  Buckets are created lazily on
    first access with the configured (or default) rate.

    Args:
        default_rpm: Default requests per minute allowed per provider.
        provider_limits: Optional mapping of provider name to its
            specific requests-per-minute limit.

    Example::

        limiter = RateLimiter(default_rpm=60)
        if limiter.acquire("openai"):
            # safe to call the provider
            ...
        else:
            limiter.wait("openai")
            # now safe
    """

    def __init__(
        self,
        default_rpm: int = 60,
        provider_limits: Optional[Dict[str, int]] = None,
    ) -> None:
        if default_rpm <= 0:
            raise ValueError("default_rpm must be a positive integer.")
        self._default_rpm = default_rpm
        self._provider_limits: Dict[str, int] = {
            k.lower().strip(): v
            for k, v in (provider_limits or {}).items()
        }
        self._buckets: Dict[str, _Bucket] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_bucket(self, provider: str) -> _Bucket:
        """Return (or lazily create) the bucket for *provider*.

        Args:
            provider: Normalised provider name.

        Returns:
            The ``_Bucket`` instance for the provider.
        """
        if provider not in self._buckets:
            rpm = self._provider_limits.get(provider, self._default_rpm)
            capacity = float(rpm)
            refill_rate = rpm / 60.0  # tokens per second
            self._buckets[provider] = _Bucket(
                capacity=capacity,
                tokens=capacity,
                refill_rate=refill_rate,
            )
        return self._buckets[provider]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self, provider: str) -> bool:
        """Attempt to consume one token from the provider's bucket.

        This is a **non-blocking** call.

        Args:
            provider: Provider name (case-insensitive).

        Returns:
            ``True`` if a token was available and consumed, ``False``
            if the caller should back off or wait.
        """
        provider = provider.lower().strip()
        with self._lock:
            bucket = self._get_bucket(provider)
            bucket.refill()
            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return True
            return False

    def wait(self, provider: str) -> None:
        """Block until a token becomes available, then consume it.

        Uses a short-sleep polling loop to avoid busy-waiting while
        keeping latency low.

        Args:
            provider: Provider name (case-insensitive).
        """
        provider = provider.lower().strip()
        while True:
            with self._lock:
                bucket = self._get_bucket(provider)
                bucket.refill()
                if bucket.tokens >= 1.0:
                    bucket.tokens -= 1.0
                    return
                # Calculate how long until at least one token is available
                deficit = 1.0 - bucket.tokens
                wait_seconds = deficit / bucket.refill_rate
            # Sleep outside the lock so other threads can proceed
            time.sleep(min(wait_seconds, 0.1))

    def get_remaining(self, provider: str) -> int:
        """Return the approximate number of tokens available right now.

        Args:
            provider: Provider name (case-insensitive).

        Returns:
            Integer count of remaining tokens (floored).
        """
        provider = provider.lower().strip()
        with self._lock:
            bucket = self._get_bucket(provider)
            bucket.refill()
            return int(bucket.tokens)

    def set_limit(self, provider: str, rpm: int) -> None:
        """Update the rate limit for a specific provider.

        If the provider already has a bucket, it is replaced with a
        fresh one at the new rate.

        Args:
            provider: Provider name.
            rpm: New requests-per-minute limit.

        Raises:
            ValueError: If *rpm* is not positive.
        """
        if rpm <= 0:
            raise ValueError("rpm must be a positive integer.")
        provider = provider.lower().strip()
        with self._lock:
            self._provider_limits[provider] = rpm
            # Reset the bucket so the new limit takes effect immediately
            capacity = float(rpm)
            self._buckets[provider] = _Bucket(
                capacity=capacity,
                tokens=capacity,
                refill_rate=rpm / 60.0,
            )

    def reset(self, provider: str | None = None) -> None:
        """Reset bucket(s) to full capacity.

        Args:
            provider: If given, reset only this provider's bucket.
                If ``None``, reset all buckets.
        """
        with self._lock:
            if provider is not None:
                provider = provider.lower().strip()
                if provider in self._buckets:
                    bucket = self._buckets[provider]
                    bucket.tokens = bucket.capacity
                    bucket.last_refill = time.monotonic()
            else:
                for bucket in self._buckets.values():
                    bucket.tokens = bucket.capacity
                    bucket.last_refill = time.monotonic()
