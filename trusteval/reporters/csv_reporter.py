# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""CSV report generator for TrustEval evaluation results.

Produces a CSV file with a summary header row followed by per-test-case
detail rows.  All values are properly escaped per RFC 4180.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from trusteval.reporters.base_reporter import BaseReporter


class CSVReporter(BaseReporter):
    """Generate evaluation reports in CSV format.

    The output consists of two sections:

    1. **Summary row** — overall score, grade, trust level, and pillar
       breakdown (columns prefixed with ``pillar_``).
    2. **Test-case rows** — one row per test case with columns for
       pillar, prompt, response, score, and pass/fail flag.

    Args:
        evaluation_result: The evaluation result dict.

    Example::

        reporter = CSVReporter(result)
        path = reporter.generate("reports/eval_001.csv")
    """

    def generate(self, output_path: str | Path) -> str:
        """Write the evaluation result to a CSV file.

        Args:
            output_path: Destination file path (with ``.csv`` extension).

        Returns:
            Absolute path to the generated CSV file.

        Raises:
            OSError: If the file cannot be written.
        """
        output_path = Path(output_path)
        self._ensure_parent_dir(output_path)

        with open(output_path, "w", newline="", encoding="utf-8-sig") as fh:
            self._write_summary_section(fh)
            fh.write("\n")  # blank line separator
            self._write_test_cases_section(fh)

        return str(output_path.resolve())

    # ------------------------------------------------------------------
    # Internal writers
    # ------------------------------------------------------------------

    def _write_summary_section(self, fh: io.TextIOBase) -> None:
        """Write the summary header and row.

        Args:
            fh: Open file handle to write to.
        """
        pillar_results = self._get_pillar_results()
        metadata = self._get_metadata()

        # Build dynamic pillar columns
        pillar_names = [p.get("name", f"pillar_{i}") for i, p in enumerate(pillar_results)]

        headers = [
            "report_type",
            "generated_at",
            "provider",
            "model",
            "overall_score",
            "overall_score_pct",
            "grade",
            "trust_level",
        ]
        headers.extend(f"pillar_{name}_score" for name in pillar_names)
        headers.extend(f"pillar_{name}_grade" for name in pillar_names)

        writer = csv.writer(fh)
        writer.writerow(headers)

        row = [
            "summary",
            datetime.now(timezone.utc).isoformat(),
            metadata.get("provider", ""),
            metadata.get("model", ""),
            self.result.get("overall_score", ""),
            self.format_score(self.result.get("overall_score")),
            self.format_grade(self.result.get("grade")),
            self.result.get("trust_level", ""),
        ]
        for pillar in pillar_results:
            row.append(pillar.get("score", ""))
        for pillar in pillar_results:
            row.append(self.format_grade(pillar.get("grade")))

        writer.writerow(row)

    def _write_test_cases_section(self, fh: io.TextIOBase) -> None:
        """Write the per-test-case detail rows.

        Args:
            fh: Open file handle to write to.
        """
        test_cases = self._get_test_cases()
        if not test_cases:
            return

        # Determine columns from the union of all test-case keys
        all_keys: list[str] = []
        seen: set[str] = set()
        # Preferred column order
        preferred = ["id", "pillar", "prompt", "response", "score", "passed", "reason"]
        for key in preferred:
            for tc in test_cases:
                if key in tc and key not in seen:
                    all_keys.append(key)
                    seen.add(key)
                    break
        # Remaining keys in alphabetical order
        for tc in test_cases:
            for key in sorted(tc.keys()):
                if key not in seen:
                    all_keys.append(key)
                    seen.add(key)

        writer = csv.writer(fh)
        writer.writerow(all_keys)

        for tc in test_cases:
            row = [self._format_cell(tc.get(key, "")) for key in all_keys]
            writer.writerow(row)

    @staticmethod
    def _format_cell(value: Any) -> str:
        """Convert any value to a CSV-safe string.

        Args:
            value: The cell value.

        Returns:
            String representation suitable for CSV.
        """
        if value is None:
            return ""
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, (dict, list)):
            import json
            return json.dumps(value, ensure_ascii=False, default=str)
        return str(value)
