# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Comprehensive PII regex patterns and validation functions.

Provides pattern definitions for detecting personally identifiable
information (PII) in text, along with validation helpers such as the
Luhn algorithm for credit card number verification.
"""

from __future__ import annotations

import re
from typing import Dict, List

# ---------------------------------------------------------------------------
# Core PII regex patterns
# ---------------------------------------------------------------------------

PII_PATTERNS: Dict[str, str] = {
    # US Social Security Number
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    # Credit card (with spaces or dashes)
    "credit_card": r"\b\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b",
    # Credit card (contiguous 13-19 digits)
    "credit_card_raw": r"\b\d{13,19}\b",
    # International Bank Account Number
    "iban": r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b",
    # Email address
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    # US phone number
    "phone_us": r"\b(\+1)?\s?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b",
    # International phone (E.164-ish)
    "phone_intl": r"\b\+\d{1,3}[\s.-]?\d{2,4}[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b",
    # Medical Record Number
    "medical_id": r"\bMRN[\s:-]?\d{6,10}\b",
    # IPv4 address
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    # Passport number (common format: letter + 8 digits)
    "passport": r"\b[A-Z]\d{8}\b",
    # US Driver's license (letter + 7-12 digits)
    "drivers_license": r"\b[A-Z]\d{7,12}\b",
    # Date of birth patterns
    "date_of_birth": r"\b(?:DOB|Date of Birth|Born)[\s:]*\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b",
    # US ZIP code
    "zip_code": r"\b\d{5}(?:-\d{4})?\b",
    # Bank routing number (9 digits)
    "routing_number": r"\b\d{9}\b",
    # US Employer Identification Number
    "ein": r"\b\d{2}-\d{7}\b",
    # AWS access key
    "aws_key": r"\bAKIA[0-9A-Z]{16}\b",
    # Generic API key pattern
    "api_key": r"\b(?:api[_-]?key|apikey|token)[\s:=]+[A-Za-z0-9_\-]{20,}\b",
    # Street address (simplified)
    "street_address": r"\b\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Dr|Drive|Rd|Road|Ln|Lane|Ct|Court|Way|Pl|Place)\b",
    # Full name pattern (Title + Name)
    "full_name_title": r"\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b",
}

# Compiled patterns for efficient reuse
COMPILED_PATTERNS: Dict[str, re.Pattern] = {
    name: re.compile(pattern, re.IGNORECASE if name in {"email", "date_of_birth", "api_key"} else 0)
    for name, pattern in PII_PATTERNS.items()
}


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


def luhn_check(number: str) -> bool:
    """Validate a number string using the Luhn algorithm.

    The Luhn algorithm is used to validate credit card numbers, IMEI
    numbers, and other identification numbers.

    Args:
        number: A string of digits (spaces and dashes are stripped).

    Returns:
        True if the number passes the Luhn check.
    """
    digits = re.sub(r"[\s-]", "", number)
    if not digits.isdigit() or len(digits) < 2:
        return False

    total = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def validate_ssn(ssn: str) -> bool:
    """Validate a US Social Security Number format.

    Checks that the SSN is not in a known-invalid range (e.g., area
    number 000, 666, or 900-999).

    Args:
        ssn: SSN string in ``XXX-XX-XXXX`` format.

    Returns:
        True if the SSN format is valid.
    """
    match = re.fullmatch(r"(\d{3})-(\d{2})-(\d{4})", ssn)
    if not match:
        return False
    area, group, serial = match.groups()
    # Invalid area numbers
    if area in ("000", "666") or area.startswith("9"):
        return False
    if group == "00" or serial == "0000":
        return False
    return True


def validate_email(email: str) -> bool:
    """Basic email format validation.

    Args:
        email: Email address string.

    Returns:
        True if the email has a valid-looking format.
    """
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"
    return bool(re.fullmatch(pattern, email))


def validate_ip_address(ip: str) -> bool:
    """Validate an IPv4 address.

    Args:
        ip: IP address string.

    Returns:
        True if all octets are in range 0-255.
    """
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True


def validate_credit_card(number: str) -> bool:
    """Validate a credit card number using Luhn and length checks.

    Args:
        number: Credit card number string.

    Returns:
        True if the number passes validation.
    """
    digits = re.sub(r"[\s-]", "", number)
    if not digits.isdigit():
        return False
    if len(digits) < 13 or len(digits) > 19:
        return False
    return luhn_check(digits)


def scan_text(text: str) -> List[Dict[str, str]]:
    """Scan text for all PII pattern matches.

    Args:
        text: The text to scan.

    Returns:
        List of dicts with keys ``"type"``, ``"value"``, ``"start"``,
        ``"end"`` for each match.
    """
    findings: List[Dict[str, str]] = []
    for pii_type, compiled in COMPILED_PATTERNS.items():
        for match in compiled.finditer(text):
            value = match.group()
            # Apply additional validation for types that need it
            if pii_type in ("credit_card", "credit_card_raw"):
                if not validate_credit_card(value):
                    continue
            if pii_type == "ssn":
                if not validate_ssn(value):
                    continue
            if pii_type == "ip_address":
                if not validate_ip_address(value):
                    continue
            findings.append({
                "type": pii_type,
                "value": value,
                "start": str(match.start()),
                "end": str(match.end()),
            })
    return findings
