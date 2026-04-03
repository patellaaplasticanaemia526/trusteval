# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Tamper-evident audit logging for TrustEval operations.

Each log entry includes a SHA-256 hash of the previous entry, forming a
hash chain that makes undetected modification of historical records
computationally infeasible.  Logs are rotated daily with a configurable
retention period.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

_TRUSTEVAL_DIR = Path.home() / ".trusteval"
_AUDIT_LOG_PATH = _TRUSTEVAL_DIR / "audit.log"
_RETENTION_DAYS = 30


class AuditLogger:
    """Tamper-evident audit logger with hash-chained entries.

    Every entry written to the audit log carries a SHA-256 hash of the
    preceding entry.  This enables detection of any retroactive
    modification or deletion of log records.

    Args:
        log_path: Filesystem path for the audit log file.
        retention_days: Number of days to keep rotated log files.

    Example::

        audit = AuditLogger()
        audit.log_evaluation_start("eval-001", {"model": "gpt-4"})
        audit.log_evaluation_complete("eval-001", {"score": 0.87})
    """

    def __init__(
        self,
        log_path: Path | str | None = None,
        retention_days: int = _RETENTION_DAYS,
    ) -> None:
        self._log_path = Path(log_path) if log_path else _AUDIT_LOG_PATH
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._retention_days = retention_days
        self._lock = threading.Lock()

        # Hash chain state — seed with zeros for the very first entry
        self._previous_hash: str = "0" * 64

        # Initialise chain from existing log file if present
        self._init_chain_from_existing()

        # Set up Python logging with daily rotation
        self._logger = logging.getLogger(f"trusteval.audit.{id(self)}")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        if not self._logger.handlers:
            handler = TimedRotatingFileHandler(
                filename=str(self._log_path),
                when="midnight",
                interval=1,
                backupCount=retention_days,
                encoding="utf-8",
                utc=True,
            )
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_chain_from_existing(self) -> None:
        """Resume the hash chain from the last entry in an existing log."""
        if not self._log_path.is_file():
            return
        try:
            with open(self._log_path, "r", encoding="utf-8") as fh:
                last_line: str = ""
                for line in fh:
                    stripped = line.strip()
                    if stripped:
                        last_line = stripped
            if last_line:
                self._previous_hash = hashlib.sha256(
                    last_line.encode("utf-8")
                ).hexdigest()
        except Exception:
            # If we cannot read the existing log, start a fresh chain
            self._previous_hash = "0" * 64

    def _compute_hash(self, entry_json: str) -> str:
        """Compute SHA-256 hash of a serialised log entry.

        Args:
            entry_json: JSON string of the entry.

        Returns:
            Hex-encoded SHA-256 digest.
        """
        return hashlib.sha256(entry_json.encode("utf-8")).hexdigest()

    def _write_entry(
        self,
        event_type: str,
        details: Dict[str, Any],
        entry_id: Optional[str] = None,
    ) -> str:
        """Build, hash-chain, and write a single audit entry.

        Args:
            event_type: Category label for the event.
            details: Arbitrary key-value payload.
            entry_id: Optional caller-provided entry identifier.

        Returns:
            The unique ID assigned to the entry.
        """
        eid = entry_id or uuid4().hex[:12]
        timestamp = datetime.now(timezone.utc).isoformat()

        with self._lock:
            entry: Dict[str, Any] = {
                "id": eid,
                "timestamp": timestamp,
                "event_type": event_type,
                "previous_hash": self._previous_hash,
                "details": details,
            }
            entry_json = json.dumps(entry, separators=(",", ":"), sort_keys=True)
            entry["entry_hash"] = self._compute_hash(entry_json)

            # Serialise the final entry (with its own hash appended)
            final_json = json.dumps(entry, separators=(",", ":"), sort_keys=True)
            self._logger.info(final_json)
            self._previous_hash = self._compute_hash(final_json)

        return eid

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_evaluation_start(
        self,
        eval_id: str,
        config: Dict[str, Any],
    ) -> None:
        """Record the start of an evaluation run.

        Args:
            eval_id: Unique evaluation identifier.
            config: Configuration snapshot for the evaluation.
        """
        self._write_entry(
            event_type="evaluation_start",
            details={"eval_id": eval_id, "config": config},
            entry_id=eval_id,
        )

    def log_evaluation_complete(
        self,
        eval_id: str,
        result: Dict[str, Any],
    ) -> None:
        """Record the completion of an evaluation run.

        Args:
            eval_id: The same identifier passed to ``log_evaluation_start``.
            result: Summary result payload (scores, grade, etc.).
        """
        self._write_entry(
            event_type="evaluation_complete",
            details={"eval_id": eval_id, "result": result},
            entry_id=eval_id,
        )

    def log_key_access(
        self,
        provider: str,
        masked_key: str,
    ) -> None:
        """Record an API-key retrieval event.

        Args:
            provider: Provider whose key was accessed.
            masked_key: Masked representation of the key (never log raw keys).
        """
        self._write_entry(
            event_type="key_access",
            details={"provider": provider, "masked_key": masked_key},
        )

    def log_auth_failure(
        self,
        ip: str,
        reason: str,
    ) -> None:
        """Record an authentication or authorisation failure.

        Args:
            ip: Source IP address or identifier.
            reason: Human-readable failure reason.
        """
        self._write_entry(
            event_type="auth_failure",
            details={"ip": ip, "reason": reason},
        )

    def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
    ) -> None:
        """Record an arbitrary security-relevant event.

        Args:
            event_type: Descriptive category (e.g. ``"injection_detected"``).
            details: Structured context for the event.
        """
        self._write_entry(
            event_type=event_type,
            details=details,
        )

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire audit log hash chain.

        Reads the log file sequentially and checks that each entry's
        ``previous_hash`` matches the SHA-256 of the preceding entry.

        Returns:
            ``True`` if the chain is intact, ``False`` if tampering is
            detected or the log is unreadable.
        """
        if not self._log_path.is_file():
            return True  # No log yet is vacuously correct

        try:
            previous_hash = "0" * 64
            with open(self._log_path, "r", encoding="utf-8") as fh:
                for line_no, line in enumerate(fh, start=1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    entry = json.loads(stripped)
                    if entry.get("previous_hash") != previous_hash:
                        return False
                    previous_hash = self._compute_hash(stripped)
            return True
        except Exception:
            return False
