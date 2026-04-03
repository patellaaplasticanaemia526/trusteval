# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""JSON report generator for TrustEval evaluation results.

Produces a well-structured, pretty-printed JSON file containing the
complete evaluation output.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from trusteval.reporters.base_reporter import BaseReporter


class JSONReporter(BaseReporter):
    """Generate evaluation reports in JSON format.

    The output file is pretty-printed with 2-space indentation and
    contains the full evaluation result augmented with report metadata.

    Args:
        evaluation_result: The evaluation result dict.

    Example::

        reporter = JSONReporter(result)
        path = reporter.generate("reports/eval_001.json")
    """

    def generate(self, output_path: str | Path) -> str:
        """Write the evaluation result to a JSON file.

        Args:
            output_path: Destination file path (with ``.json`` extension).

        Returns:
            Absolute path to the generated JSON file.

        Raises:
            OSError: If the file cannot be written.
        """
        output_path = Path(output_path)
        self._ensure_parent_dir(output_path)

        report: Dict[str, Any] = {
            "report_format": "trusteval_json",
            "report_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "overall_score": self.result.get("overall_score"),
                "overall_score_pct": self.format_score(
                    self.result.get("overall_score")
                ),
                "grade": self.format_grade(self.result.get("grade")),
                "trust_level": self.result.get("trust_level", "N/A"),
            },
            "metadata": self._get_metadata(),
            "pillar_results": self._get_pillar_results(),
            "flagged_items": self._get_flagged_items(),
            "test_cases": self._get_test_cases(),
            "raw_result": self.result,
        }

        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False, default=str)

        return str(output_path.resolve())
