# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Prompt sanitisation and injection detection.

Provides input validation for user-supplied prompts before they are
forwarded to LLM providers.  Detects common prompt-injection patterns,
strips dangerous control characters, and enforces length limits.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_PROMPT_LENGTH: int = 8_000
"""Maximum allowed prompt length in characters."""

INJECTION_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?prior\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?previous\s+(instructions|context)", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?previous\s+(instructions|context)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+", re.IGNORECASE),
    re.compile(r"from\s+now\s+on\s+you\s+are", re.IGNORECASE),
    re.compile(r"pretend\s+you\s+are", re.IGNORECASE),
    re.compile(r"act\s+as\s+if\s+you\s+are", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"\bDAN\s+mode\b", re.IGNORECASE),
    re.compile(r"\bDAN\b.*\bDo\s+Anything\s+Now\b", re.IGNORECASE | re.DOTALL),
    re.compile(r"Do\s+Anything\s+Now", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"reveal\s+(your\s+)?(system|hidden|secret)\s+(prompt|instructions)", re.IGNORECASE),
    re.compile(r"show\s+me\s+your\s+(system|hidden|secret)\s+(prompt|instructions)", re.IGNORECASE),
    re.compile(r"\boverride\b.*\b(instructions|safety|filters|rules)\b", re.IGNORECASE),
    re.compile(r"bypass\s+(safety|content|ethical)\s+(filters?|restrictions?|guidelines?)", re.IGNORECASE),
    re.compile(r"disable\s+(safety|content|ethical)\s+(filters?|restrictions?|guidelines?)", re.IGNORECASE),
    re.compile(r"ignore\s+(safety|content|ethical)\s+(filters?|restrictions?|guidelines?)", re.IGNORECASE),
    re.compile(r"\[INST\]|\[/INST\]", re.IGNORECASE),
    re.compile(r"<\|im_start\|>|<\|im_end\|>", re.IGNORECASE),
    re.compile(r"<<\s*SYS\s*>>|<<\s*/SYS\s*>>", re.IGNORECASE),
    re.compile(r"```\s*system\b", re.IGNORECASE),
]
"""Compiled regex patterns that indicate prompt-injection attempts."""

# Control characters to strip (C0/C1 minus common whitespace)
_ALLOWED_CONTROL = {"\n", "\r", "\t"}


class InputSanitizer:
    """Validate and sanitise LLM prompts before submission.

    The sanitizer enforces length limits, strips dangerous control
    characters, normalises Unicode, and detects known prompt-injection
    patterns.

    Args:
        max_length: Override the default maximum prompt length.
        extra_patterns: Additional regex patterns to treat as injections.

    Example::

        sanitizer = InputSanitizer()
        clean = sanitizer.sanitize(user_input)
        if sanitizer.detect_injection(clean):
            raise SecurityError("Injection detected")
    """

    def __init__(
        self,
        max_length: int = MAX_PROMPT_LENGTH,
        extra_patterns: List[re.Pattern[str]] | None = None,
    ) -> None:
        self.max_length = max_length
        self._patterns: List[re.Pattern[str]] = list(INJECTION_PATTERNS)
        if extra_patterns:
            self._patterns.extend(extra_patterns)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sanitize(self, prompt: str) -> str:
        """Clean a raw prompt string for safe LLM submission.

        Processing steps:

        1. Validate UTF-8 encoding (re-encode/decode to catch surrogates).
        2. Strip null bytes and non-whitelisted control characters.
        3. Normalise Unicode to NFC form.
        4. Collapse excessive whitespace runs.
        5. Truncate to ``max_length``.

        Args:
            prompt: The raw prompt text.

        Returns:
            The sanitised prompt string.

        Raises:
            TypeError: If *prompt* is not a string.
        """
        if not isinstance(prompt, str):
            raise TypeError(
                f"Expected str, got {type(prompt).__name__}"
            )

        # 1. Validate / normalise UTF-8
        text = prompt.encode("utf-8", errors="replace").decode("utf-8")

        # 2. Strip null bytes and dangerous control characters
        text = text.replace("\x00", "")
        cleaned_chars: list[str] = []
        for ch in text:
            if unicodedata.category(ch).startswith("C") and ch not in _ALLOWED_CONTROL:
                continue  # drop control characters
            cleaned_chars.append(ch)
        text = "".join(cleaned_chars)

        # 3. Unicode NFC normalisation
        text = unicodedata.normalize("NFC", text)

        # 4. Collapse runs of whitespace (preserve newlines)
        text = re.sub(r"[^\S\n]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        # 5. Enforce length limit
        if len(text) > self.max_length:
            text = text[: self.max_length]

        return text

    def detect_injection(self, prompt: str) -> bool:
        """Check whether a prompt contains known injection patterns.

        Args:
            prompt: The prompt text to analyse.  Should be sanitised
                first for best results.

        Returns:
            ``True`` if one or more injection patterns are detected.
        """
        for pattern in self._patterns:
            if pattern.search(prompt):
                return True
        return False

    def validate_prompt(self, prompt: str) -> Tuple[bool, str]:
        """Perform full validation on a prompt and return a verdict.

        Runs sanitisation, length checks, and injection detection.  This
        is the recommended single entry-point for prompt validation.

        Args:
            prompt: The raw prompt text.

        Returns:
            A ``(is_valid, reason)`` tuple.  When ``is_valid`` is
            ``True``, *reason* is ``"ok"``.  Otherwise *reason*
            describes the first validation failure.
        """
        if not isinstance(prompt, str):
            return False, f"Prompt must be a string, got {type(prompt).__name__}."

        if not prompt.strip():
            return False, "Prompt is empty or contains only whitespace."

        # Length check on raw input (before sanitisation)
        if len(prompt) > self.max_length:
            return False, (
                f"Prompt exceeds maximum length of {self.max_length:,} characters "
                f"(received {len(prompt):,})."
            )

        # Sanitise
        clean = self.sanitize(prompt)

        # Injection detection
        if self.detect_injection(clean):
            # Identify which pattern(s) matched for the reason string
            matched: list[str] = []
            for pattern in self._patterns:
                match = pattern.search(clean)
                if match:
                    matched.append(match.group(0)[:50])
            reason = (
                "Potential prompt-injection detected. "
                f"Matched pattern(s): {matched}"
            )
            return False, reason

        return True, "ok"
