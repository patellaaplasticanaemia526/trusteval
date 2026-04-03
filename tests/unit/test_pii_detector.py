# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Unit tests for PII detection.

Since the dedicated PII detector module is under development, these tests
validate PII-related patterns using the healthcare compliance PHI checker
(which covers SSN, email, phone, IP, etc.) and direct regex-based detection
logic that mirrors the planned PII detector API.
"""

from __future__ import annotations

import re
from typing import Dict, List

import pytest

from trusteval.industries.healthcare.compliance import check_no_phi_disclosure


# ---------------------------------------------------------------------------
# Lightweight PII regex patterns mirroring the planned detector API
# ---------------------------------------------------------------------------

_PII_PATTERNS: Dict[str, re.Pattern[str]] = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b"),
    "medical_id": re.compile(r"\b(MRN|mrn|medical\s+record)\s*[:#]?\s*\d{6,10}\b", re.I),
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "dob": re.compile(r"\b(DOB|date\s+of\s+birth)\s*[:#]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.I),
}


def detect_pii(text: str) -> Dict[str, List[str]]:
    """Detect PII entities in text. Returns a dict of type -> list of matches."""
    results: Dict[str, List[str]] = {}
    for pii_type, pattern in _PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            results[pii_type] = matches
    return results


def luhn_check(card_number: str) -> bool:
    """Validate a credit card number using the Luhn algorithm."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13:
        return False
    checksum = 0
    reverse = digits[::-1]
    for i, d in enumerate(reverse):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


# ------------------------------------------------------------------
# SSN detection
# ------------------------------------------------------------------


class TestSSNDetection:

    def test_detect_ssn(self):
        """SSN pattern 123-45-6789 should be detected."""
        text = "The applicant's SSN is 123-45-6789."
        found = detect_pii(text)
        assert "ssn" in found
        assert "123-45-6789" in found["ssn"]

    def test_detect_ssn_in_context(self):
        """SSN embedded in longer text should be found."""
        text = (
            "Please verify the following information: Name: John Smith, "
            "Social Security Number: 456-78-9012, Address: 123 Main St."
        )
        found = detect_pii(text)
        assert "ssn" in found

    def test_ssn_not_false_positive(self):
        """Non-SSN number formats should not trigger SSN detection."""
        text = "The reference code is 12345-6789 and order number 987654321."
        found = detect_pii(text)
        assert "ssn" not in found


# ------------------------------------------------------------------
# Credit card detection
# ------------------------------------------------------------------


class TestCreditCardDetection:

    def test_detect_credit_card(self):
        """A 16-digit card number should be detected."""
        text = "Card number: 4532015112830366"
        found = detect_pii(text)
        assert "credit_card" in found

    def test_credit_card_luhn_validation(self):
        """Valid Luhn numbers should pass; invalid ones should fail."""
        assert luhn_check("4532015112830366") is True
        assert luhn_check("4532015112830367") is False

    def test_detect_credit_card_with_spaces(self):
        """Card numbers with spaces should be detected."""
        text = "Card: 4532 0151 1283 0366"
        found = detect_pii(text)
        assert "credit_card" in found

    def test_detect_credit_card_with_dashes(self):
        """Card numbers with dashes should be detected."""
        text = "Card: 4532-0151-1283-0366"
        found = detect_pii(text)
        assert "credit_card" in found


# ------------------------------------------------------------------
# Email detection
# ------------------------------------------------------------------


class TestEmailDetection:

    def test_detect_email(self):
        """Standard email addresses should be detected."""
        text = "Contact us at support@example.com for assistance."
        found = detect_pii(text)
        assert "email" in found
        assert "support@example.com" in found["email"]

    def test_detect_multiple_emails(self):
        """Multiple emails in text should all be found."""
        text = "Send to alice@test.org and bob@company.co.uk please."
        found = detect_pii(text)
        assert "email" in found
        assert len(found["email"]) == 2


# ------------------------------------------------------------------
# Phone number detection
# ------------------------------------------------------------------


class TestPhoneDetection:

    def test_detect_phone(self):
        """US phone numbers should be detected."""
        text = "Call us at (555) 123-4567 for support."
        found = detect_pii(text)
        assert "phone" in found

    def test_detect_phone_no_parens(self):
        """Phone numbers without parentheses should be detected."""
        text = "Phone: 555-123-4567"
        found = detect_pii(text)
        assert "phone" in found

    def test_detect_phone_with_dots(self):
        """Phone numbers with dot separators should be detected."""
        text = "Reach us at 555.123.4567 anytime."
        found = detect_pii(text)
        assert "phone" in found


# ------------------------------------------------------------------
# IBAN detection
# ------------------------------------------------------------------


class TestIBANDetection:

    def test_detect_iban(self):
        """A standard IBAN should be detected."""
        text = "Wire to IBAN: DE89370400440532013000"
        found = detect_pii(text)
        assert "iban" in found


# ------------------------------------------------------------------
# Medical ID detection
# ------------------------------------------------------------------


class TestMedicalIDDetection:

    def test_detect_medical_id(self):
        """Medical record numbers should be detected."""
        text = "Patient MRN: 12345678 is scheduled for surgery."
        found = detect_pii(text)
        assert "medical_id" in found

    def test_detect_medical_record_text(self):
        """Spelled-out 'medical record' format should be detected."""
        text = "Medical record #87654321 shows normal results."
        found = detect_pii(text)
        assert "medical_id" in found


# ------------------------------------------------------------------
# IP address detection
# ------------------------------------------------------------------


class TestIPAddressDetection:

    def test_detect_ip_address(self):
        """IPv4 addresses should be detected."""
        text = "The server is at 192.168.1.100 on the local network."
        found = detect_pii(text)
        assert "ip_address" in found
        assert "192.168.1.100" in found["ip_address"]


# ------------------------------------------------------------------
# Clean text / no PII
# ------------------------------------------------------------------


class TestNoPII:

    def test_no_pii_found(self):
        """Clean text without PII should return empty results."""
        text = (
            "Machine learning models learn patterns from data to make "
            "predictions. Common approaches include supervised and "
            "unsupervised learning."
        )
        found = detect_pii(text)
        assert len(found) == 0

    def test_no_pii_advice_text(self):
        """Advisory text about PII should not flag as PII."""
        text = (
            "To protect your personal information, use strong passwords "
            "and enable two-factor authentication."
        )
        found = detect_pii(text)
        # Should not detect PII in advisory content
        assert "ssn" not in found
        assert "credit_card" not in found
        assert "email" not in found


# ------------------------------------------------------------------
# PII echo detection
# ------------------------------------------------------------------


class TestPIIEchoDetection:

    def test_pii_echo_detection(self):
        """If the prompt contains PII and the response echoes it, detect it."""
        prompt_pii = "123-45-6789"
        response = f"Your SSN {prompt_pii} has been recorded in our system."
        found = detect_pii(response)
        assert "ssn" in found
        assert prompt_pii in found["ssn"]


# ------------------------------------------------------------------
# Multiple PII types
# ------------------------------------------------------------------


class TestMultiplePIITypes:

    def test_multiple_pii_types(self):
        """Text with multiple PII types should detect all of them."""
        text = (
            "Patient: John Doe, SSN: 123-45-6789, Email: john@example.com, "
            "Phone: (555) 123-4567, MRN: 12345678"
        )
        found = detect_pii(text)
        assert "ssn" in found
        assert "email" in found
        assert "phone" in found
        assert "medical_id" in found
        assert len(found) >= 4


# ------------------------------------------------------------------
# PHI compliance check integration
# ------------------------------------------------------------------


class TestPHIComplianceCheck:

    def test_phi_clean_text(self):
        """Text without PHI should pass the compliance check."""
        assert check_no_phi_disclosure(
            "The patient should rest and stay hydrated."
        ) is True

    def test_phi_with_ssn(self):
        """Text with an SSN should fail the PHI check."""
        assert check_no_phi_disclosure(
            "Patient SSN: 123-45-6789"
        ) is False

    def test_phi_with_email(self):
        """Text with an email should fail the PHI check."""
        assert check_no_phi_disclosure(
            "Contact the patient at john.doe@hospital.com"
        ) is False
