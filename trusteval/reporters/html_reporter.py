# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""HTML report generator for TrustEval evaluation results.

Produces a standalone HTML file with inline CSS using TrustEval brand
colours.  Includes score gauges, pillar breakdown tables, and flagged
items — designed for an enterprise-grade presentation.
"""

from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from trusteval.reporters.base_reporter import BaseReporter

# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------

_PRIMARY = "#0F172A"
_ACCENT = "#6366F1"
_SUCCESS = "#10B981"
_WARNING = "#F59E0B"
_DANGER = "#EF4444"
_LIGHT_BG = "#F8FAFC"
_CARD_BG = "#FFFFFF"
_BORDER = "#E2E8F0"
_TEXT = "#334155"
_TEXT_MUTED = "#64748B"


class HTMLReporter(BaseReporter):
    """Generate a standalone HTML evaluation report.

    The report uses inline CSS (no external dependencies) and is styled
    with the TrustEval brand palette.

    Args:
        evaluation_result: The evaluation result dict.

    Example::

        reporter = HTMLReporter(result)
        path = reporter.generate("reports/eval_001.html")
    """

    def generate(self, output_path: str | Path) -> str:
        """Write the evaluation result to an HTML file.

        Args:
            output_path: Destination file path (with ``.html`` extension).

        Returns:
            Absolute path to the generated HTML file.

        Raises:
            OSError: If the file cannot be written.
        """
        output_path = Path(output_path)
        self._ensure_parent_dir(output_path)

        html_content = self._render()
        output_path.write_text(html_content, encoding="utf-8")
        return str(output_path.resolve())

    def render_html(self) -> str:
        """Return the full HTML document as a string.

        This is useful for the PDF reporter which reuses the HTML
        template without writing to disk first.

        Returns:
            Complete HTML document string.
        """
        return self._render()

    # ------------------------------------------------------------------
    # Internal rendering
    # ------------------------------------------------------------------

    def _render(self) -> str:
        """Assemble the full HTML document."""
        metadata = self._get_metadata()
        overall_score = self.result.get("overall_score")
        grade = self.result.get("grade")
        trust_level = self.result.get("trust_level", "N/A")
        pillar_results = self._get_pillar_results()
        flagged_items = self._get_flagged_items()
        test_cases = self._get_test_cases()
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TrustEval Report — {html.escape(str(metadata.get('model', 'Evaluation')))}</title>
{self._render_styles()}
</head>
<body>
{self._render_header(metadata, generated_at)}
<main class="container">
{self._render_summary_cards(overall_score, grade, trust_level)}
{self._render_score_gauge(overall_score)}
{self._render_pillar_table(pillar_results)}
{self._render_flagged_items(flagged_items)}
{self._render_test_cases(test_cases)}
</main>
{self._render_footer(generated_at)}
</body>
</html>"""

    # ------------------------------------------------------------------
    # CSS
    # ------------------------------------------------------------------

    def _render_styles(self) -> str:
        """Return the inline ``<style>`` block."""
        return f"""<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
       background: {_LIGHT_BG}; color: {_TEXT}; line-height: 1.6; }}
.container {{ max-width: 960px; margin: 0 auto; padding: 24px 16px; }}
/* Header */
.header {{ background: {_PRIMARY}; color: #fff; padding: 32px 0; }}
.header .container {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
.header h1 {{ font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
.header .meta {{ font-size: 13px; color: #94A3B8; text-align: right; }}
/* Cards */
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 24px 0; }}
.card {{ background: {_CARD_BG}; border: 1px solid {_BORDER}; border-radius: 8px; padding: 20px; text-align: center; }}
.card .label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: {_TEXT_MUTED}; margin-bottom: 8px; }}
.card .value {{ font-size: 28px; font-weight: 700; }}
.card .value.grade-a {{ color: {_SUCCESS}; }}
.card .value.grade-b {{ color: {_SUCCESS}; }}
.card .value.grade-c {{ color: {_WARNING}; }}
.card .value.grade-d {{ color: {_WARNING}; }}
.card .value.grade-f {{ color: {_DANGER}; }}
/* Gauge */
.gauge-wrapper {{ text-align: center; margin: 32px 0; }}
.gauge {{ display: inline-block; position: relative; width: 180px; height: 90px; overflow: hidden; }}
.gauge::before {{ content: ''; display: block; width: 180px; height: 180px; border-radius: 50%;
                  background: conic-gradient({_ACCENT} var(--pct), {_BORDER} var(--pct)); }}
.gauge::after {{ content: ''; position: absolute; bottom: 0; left: 18px; width: 144px; height: 72px;
                 background: {_LIGHT_BG}; border-radius: 144px 144px 0 0; }}
.gauge-label {{ font-size: 32px; font-weight: 700; margin-top: -28px; position: relative; z-index: 1; }}
/* Tables */
table {{ width: 100%; border-collapse: collapse; margin: 24px 0; background: {_CARD_BG};
         border: 1px solid {_BORDER}; border-radius: 8px; overflow: hidden; }}
th {{ background: {_PRIMARY}; color: #fff; padding: 12px 16px; text-align: left; font-size: 13px;
      text-transform: uppercase; letter-spacing: 0.5px; }}
td {{ padding: 10px 16px; border-bottom: 1px solid {_BORDER}; font-size: 14px; }}
tr:last-child td {{ border-bottom: none; }}
tr:hover td {{ background: #F1F5F9; }}
.score-bar {{ display: inline-block; height: 8px; border-radius: 4px; background: {_ACCENT}; }}
.score-bar-bg {{ display: inline-block; width: 100px; height: 8px; border-radius: 4px; background: {_BORDER}; position: relative; }}
/* Flagged items */
.section-title {{ font-size: 18px; font-weight: 600; margin: 32px 0 12px; padding-bottom: 8px; border-bottom: 2px solid {_ACCENT}; }}
.flag {{ background: #FEF2F2; border-left: 4px solid {_DANGER}; padding: 12px 16px; margin: 8px 0; border-radius: 0 6px 6px 0; font-size: 14px; }}
.flag .flag-type {{ font-weight: 600; color: {_DANGER}; }}
/* Footer */
.footer {{ text-align: center; padding: 24px 0; font-size: 12px; color: {_TEXT_MUTED}; margin-top: 48px;
           border-top: 1px solid {_BORDER}; }}
.badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
.badge-trusted {{ background: #D1FAE5; color: #065F46; }}
.badge-conditional {{ background: #FEF3C7; color: #92400E; }}
.badge-untrusted {{ background: #FEE2E2; color: #991B1B; }}
@media print {{ body {{ background: #fff; }} .container {{ max-width: 100%; }} }}
</style>"""

    # ------------------------------------------------------------------
    # Section renderers
    # ------------------------------------------------------------------

    def _render_header(self, metadata: Dict[str, Any], generated_at: str) -> str:
        provider = html.escape(str(metadata.get("provider", "N/A")))
        model = html.escape(str(metadata.get("model", "N/A")))
        return f"""<header class="header">
<div class="container">
  <h1>TrustEval Report</h1>
  <div class="meta">
    <div>Provider: <strong>{provider}</strong> | Model: <strong>{model}</strong></div>
    <div>{generated_at}</div>
  </div>
</div>
</header>"""

    def _render_summary_cards(
        self,
        overall_score: float | None,
        grade: str | None,
        trust_level: str,
    ) -> str:
        grade_str = self.format_grade(grade)
        grade_class = f"grade-{grade_str.lower()}" if grade else ""

        trust_badge_class = {
            "TRUSTED": "badge-trusted",
            "CONDITIONAL": "badge-conditional",
            "UNTRUSTED": "badge-untrusted",
        }.get(trust_level, "")

        return f"""<div class="cards">
  <div class="card">
    <div class="label">Overall Score</div>
    <div class="value">{self.format_score(overall_score)}</div>
  </div>
  <div class="card">
    <div class="label">Grade</div>
    <div class="value {grade_class}">{grade_str}</div>
  </div>
  <div class="card">
    <div class="label">Trust Level</div>
    <div class="value"><span class="badge {trust_badge_class}">{html.escape(trust_level)}</span></div>
  </div>
</div>"""

    def _render_score_gauge(self, overall_score: float | None) -> str:
        if overall_score is None:
            return ""
        pct_css = f"{overall_score * 100:.0f}%"
        return f"""<div class="gauge-wrapper">
  <div class="gauge" style="--pct: {pct_css}"></div>
  <div class="gauge-label">{self.format_score(overall_score)}</div>
</div>"""

    def _render_pillar_table(self, pillar_results: List[Dict[str, Any]]) -> str:
        if not pillar_results:
            return ""
        rows = ""
        for p in pillar_results:
            name = html.escape(str(p.get("name", "Unknown")))
            score = p.get("score")
            grade = self.format_grade(p.get("grade"))
            score_pct = f"{float(score) * 100:.0f}" if score is not None else "0"
            bar = (
                f'<div class="score-bar-bg">'
                f'<div class="score-bar" style="width: {score_pct}%"></div>'
                f'</div>'
            )
            rows += f"""<tr>
  <td>{name}</td>
  <td>{self.format_score(score)}</td>
  <td>{bar}</td>
  <td>{grade}</td>
</tr>
"""
        return f"""<h2 class="section-title">Pillar Breakdown</h2>
<table>
<thead><tr><th>Pillar</th><th>Score</th><th>Distribution</th><th>Grade</th></tr></thead>
<tbody>{rows}</tbody>
</table>"""

    def _render_flagged_items(self, flagged_items: List[Dict[str, Any]]) -> str:
        if not flagged_items:
            return ""
        items_html = ""
        for item in flagged_items:
            ftype = html.escape(str(item.get("type", item.get("pillar", "Issue"))))
            desc = html.escape(str(item.get("description", item.get("reason", "No description"))))
            severity = html.escape(str(item.get("severity", "")))
            sev_label = f" ({severity})" if severity else ""
            items_html += f'<div class="flag"><span class="flag-type">{ftype}{sev_label}:</span> {desc}</div>\n'
        return f'<h2 class="section-title">Flagged Items</h2>\n{items_html}'

    def _render_test_cases(self, test_cases: List[Dict[str, Any]]) -> str:
        if not test_cases:
            return ""
        rows = ""
        for i, tc in enumerate(test_cases, start=1):
            tc_id = html.escape(str(tc.get("id", i)))
            pillar = html.escape(str(tc.get("pillar", "")))
            prompt = html.escape(str(tc.get("prompt", ""))[:120])
            score = tc.get("score")
            passed = tc.get("passed")
            pass_str = ""
            if passed is True:
                pass_str = f'<span style="color:{_SUCCESS}; font-weight:600;">PASS</span>'
            elif passed is False:
                pass_str = f'<span style="color:{_DANGER}; font-weight:600;">FAIL</span>'
            rows += f"<tr><td>{tc_id}</td><td>{pillar}</td><td>{prompt}</td><td>{self.format_score(score)}</td><td>{pass_str}</td></tr>\n"

        return f"""<h2 class="section-title">Test Cases</h2>
<table>
<thead><tr><th>#</th><th>Pillar</th><th>Prompt</th><th>Score</th><th>Result</th></tr></thead>
<tbody>{rows}</tbody>
</table>"""

    def _render_footer(self, generated_at: str) -> str:
        return f"""<footer class="footer">
  <p>Generated by <strong>TrustEval</strong> — Enterprise LLM Evaluation Framework</p>
  <p>{generated_at}</p>
</footer>"""
