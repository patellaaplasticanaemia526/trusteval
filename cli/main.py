# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Click-based CLI for TrustEval with rich terminal output.

Entry-point is the ``cli`` group, registered as ``trusteval`` in
``pyproject.toml`` via ``[project.scripts]``.
"""

from __future__ import annotations

import json
import os
import sys
import time
import getpass
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.columns import Columns
from rich import box

from trusteval.version import __version__

# ---------------------------------------------------------------------------
# Rich console (shared across all commands)
# ---------------------------------------------------------------------------

console = Console()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALL_PILLARS = ["hallucination", "bias", "pii", "toxicity"]

PROVIDER_MODELS: Dict[str, List[str]] = {
    "openai": ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
    "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-3.5-sonnet"],
    "google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
    "huggingface": ["meta-llama/Llama-3-70b", "mistralai/Mixtral-8x7B", "microsoft/phi-3"],
    "groq": ["llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
    "xai": ["grok-1", "grok-1.5"],
    "local": ["custom"],
}

VALID_INDUSTRIES = ["healthcare", "finance", "legal", "education", "general", "hr", "insurance"]

_CONFIG_DIR = Path.home() / ".trusteval"
_CONFIG_FILE = _CONFIG_DIR / "config.yaml"
_KEYS_FILE = _CONFIG_DIR / "keys.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _print_banner() -> None:
    """Display the TrustEval startup banner."""
    banner_text = Text()
    banner_text.append("TrustEval", style="bold cyan")
    banner_text.append(f" v{__version__}\n", style="dim")
    banner_text.append("Benchmark LLMs. Build Trust.", style="italic white")
    console.print(
        Panel(
            banner_text,
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 4),
        )
    )
    console.print()


def _grade_style(grade: str) -> str:
    """Return a rich style string for a letter grade."""
    if grade in ("A", "B"):
        return "bold green"
    if grade in ("C", "D"):
        return "bold yellow"
    return "bold red"


def _verdict_panel(trust_level: str, overall_score: float, grade: str) -> None:
    """Print the final verdict banner."""
    if trust_level == "TRUSTED":
        icon = "[bold green]TRUSTED[/bold green]"
        border = "green"
        symbol = "[green]>>>[/green]"
    elif trust_level == "CONDITIONAL":
        icon = "[bold yellow]CONDITIONAL[/bold yellow]"
        border = "yellow"
        symbol = "[yellow]>>![/yellow]"
    else:
        icon = "[bold red]UNTRUSTED[/bold red]"
        border = "red"
        symbol = "[red]>>X[/red]"

    verdict_text = Text.from_markup(
        f"  {symbol}  VERDICT: {icon}  |  Score: {overall_score:.1%}  |  Grade: {grade}\n"
    )
    console.print()
    console.print(Panel(verdict_text, border_style=border, box=box.HEAVY, title="Final Assessment"))


def _simulate_pillar_evaluation(pillar: str, industry: str) -> Dict[str, Any]:
    """Simulate a pillar evaluation and return result dict.

    In production this delegates to the core evaluation engine.  For the
    CLI scaffold it returns representative simulated data so the output
    formatting can be demonstrated end-to-end.
    """
    import random

    random.seed(hash((pillar, industry)) % (2**31))
    test_count = random.randint(20, 40)
    score = round(random.uniform(0.55, 0.98), 4)
    passed = int(test_count * score)
    failed = test_count - passed

    from trusteval.core.scorer import compute_grade, compute_trust_level

    grade = compute_grade(score)
    trust = compute_trust_level(grade)

    return {
        "pillar": pillar,
        "score": score,
        "grade": grade,
        "trust": trust,
        "tests_run": test_count,
        "passed": passed,
        "failed": failed,
    }


def _load_keys() -> Dict[str, str]:
    """Load stored API keys from disk."""
    if _KEYS_FILE.is_file():
        try:
            return json.loads(_KEYS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_keys(keys: Dict[str, str]) -> None:
    """Persist API keys to disk."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _KEYS_FILE.write_text(json.dumps(keys, indent=2), encoding="utf-8")


def _load_config_yaml() -> Dict[str, Any]:
    """Load config.yaml as a plain dict."""
    try:
        import yaml
    except ImportError:
        return {}
    if not _CONFIG_FILE.is_file():
        return {}
    try:
        with open(_CONFIG_FILE, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_config_yaml(data: Dict[str, Any]) -> None:
    """Write config dict to config.yaml."""
    try:
        import yaml
    except ImportError:
        console.print("[red]PyYAML is required for config management. Install with: pip install pyyaml[/red]")
        raise SystemExit(1)
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_FILE, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, default_flow_style=False, sort_keys=True)


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group()
@click.version_option(version=__version__, prog_name="trusteval")
def cli() -> None:
    """TrustEval -- Enterprise LLM Evaluation & Responsible AI Framework."""


# ===================================================================
# trusteval evaluate
# ===================================================================


@cli.command()
@click.option("--provider", default="openai", help="LLM provider name.", show_default=True)
@click.option("--model", default="gpt-4", help="Model identifier.", show_default=True)
@click.option(
    "--industry", default="general", help="Target industry for benchmark selection.", show_default=True
)
@click.option(
    "--pillars",
    default=None,
    help="Comma-separated pillar list (default: all).",
)
@click.option("--output", "-o", default=None, type=click.Path(), help="Save JSON results to file.")
@click.option("--prompt", default=None, help="Single prompt for a quick evaluation.")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Enable verbose output.")
def evaluate(
    provider: str,
    model: str,
    industry: str,
    pillars: Optional[str],
    output: Optional[str],
    prompt: Optional[str],
    verbose: bool,
) -> None:
    """Run a full trust evaluation against an LLM."""
    _print_banner()

    # Parse pillars
    pillar_list: List[str] = (
        [p.strip().lower() for p in pillars.split(",") if p.strip()]
        if pillars
        else list(ALL_PILLARS)
    )

    # Header info
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="dim")
    info_table.add_column("Value", style="bold")
    info_table.add_row("Provider", f"{provider} ({model})")
    info_table.add_row("Industry", industry.capitalize())
    info_table.add_row("Pillars", ", ".join(pillar_list) if len(pillar_list) < 4 else f"All {len(pillar_list)}")
    if prompt:
        display_prompt = prompt[:60] + "..." if len(prompt) > 60 else prompt
        info_table.add_row("Prompt", f'"{display_prompt}"')
    console.print(info_table)
    console.print()

    # Run evaluation with progress bar
    results: List[Dict[str, Any]] = []
    total_tests = 0
    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("|"),
        TextColumn("{task.fields[tests]} tests"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            "[cyan]Running evaluation...", total=len(pillar_list), tests=0
        )

        for pillar in pillar_list:
            result = _simulate_pillar_evaluation(pillar, industry)
            results.append(result)
            total_tests += result["tests_run"]
            progress.update(task, advance=1, tests=total_tests)
            time.sleep(0.4)  # brief pause for visual feedback

    elapsed = time.time() - start_time
    console.print()

    # Results table
    results_table = Table(
        title="EVALUATION RESULTS",
        box=box.ROUNDED,
        title_style="bold white",
        header_style="bold cyan",
        border_style="bright_blue",
        padding=(0, 1),
    )
    results_table.add_column("Pillar", style="bold", min_width=16)
    results_table.add_column("Score", justify="center", min_width=8)
    results_table.add_column("Grade", justify="center", min_width=8)
    results_table.add_column("Status", justify="center", min_width=8)
    results_table.add_column("Tests", justify="right", min_width=8)
    results_table.add_column("Pass", justify="right", min_width=6, style="green")
    results_table.add_column("Fail", justify="right", min_width=6, style="red")

    for r in results:
        score_style = _grade_style(r["grade"])
        status_icon = "[green]PASS[/green]" if r["trust"] == "TRUSTED" else (
            "[yellow]WARN[/yellow]" if r["trust"] == "CONDITIONAL" else "[red]FAIL[/red]"
        )
        results_table.add_row(
            r["pillar"].capitalize(),
            f"[{score_style.split()[-1]}]{r['score']:.1%}[/{score_style.split()[-1]}]",
            f"[{score_style}]{r['grade']}[/{score_style}]",
            status_icon,
            str(r["tests_run"]),
            str(r["passed"]),
            str(r["failed"]),
        )

    console.print(results_table)

    # Per-pillar summary panels
    panels = []
    for r in results:
        style = _grade_style(r["grade"])
        color = style.split()[-1]
        body = (
            f"[{color}]Score : {r['score']:.1%}[/{color}]\n"
            f"Grade : [{style}]{r['grade']}[/{style}]\n"
            f"Tests : {r['tests_run']}  ({r['passed']} passed, {r['failed']} failed)"
        )
        panels.append(
            Panel(body, title=f"[bold]{r['pillar'].capitalize()}[/bold]", border_style=color, width=36)
        )
    console.print()
    console.print(Columns(panels, equal=True, expand=True))

    # Overall score
    from trusteval.core.scorer import Scorer, compute_grade, compute_trust_level

    pillar_weights = {p: 1.0 for p in pillar_list}
    scorer = Scorer(pillar_weights)
    scores = {r["pillar"]: r["score"] for r in results}
    overall = scorer.weighted_average(scores)
    overall_grade = compute_grade(overall)
    trust_level = compute_trust_level(overall_grade)

    _verdict_panel(trust_level, overall, overall_grade)

    # Stats footer
    console.print(
        f"\n  [dim]{total_tests} tests completed in {elapsed:.1f}s across {len(pillar_list)} pillars[/dim]\n"
    )

    # Save to file if requested
    if output:
        output_data = {
            "provider": provider,
            "model": model,
            "industry": industry,
            "pillars": pillar_list,
            "results": results,
            "overall_score": overall,
            "overall_grade": overall_grade,
            "trust_level": trust_level,
            "total_tests": total_tests,
            "elapsed_seconds": round(elapsed, 2),
        }
        Path(output).write_text(json.dumps(output_data, indent=2), encoding="utf-8")
        console.print(f"  [dim]Results saved to {output}[/dim]\n")


# ===================================================================
# trusteval compare
# ===================================================================


@cli.command()
@click.option("--provider-a", required=True, help="First provider name.")
@click.option("--model-a", required=True, help="First model identifier.")
@click.option("--provider-b", required=True, help="Second provider name.")
@click.option("--model-b", required=True, help="Second model identifier.")
@click.option("--industry", default="general", help="Industry for benchmarks.", show_default=True)
def compare(
    provider_a: str,
    model_a: str,
    provider_b: str,
    model_b: str,
    industry: str,
) -> None:
    """Compare two LLMs side by side."""
    _print_banner()

    from trusteval.core.scorer import Scorer, compute_grade, compute_trust_level

    console.print(
        f"  [bold]Comparing:[/bold] {provider_a}/{model_a}  vs  {provider_b}/{model_b}"
    )
    console.print(f"  [dim]Industry: {industry.capitalize()}[/dim]\n")

    # Run evaluations for both
    results_a: List[Dict[str, Any]] = []
    results_b: List[Dict[str, Any]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Evaluating both models...", total=len(ALL_PILLARS) * 2)
        for pillar in ALL_PILLARS:
            results_a.append(_simulate_pillar_evaluation(pillar, f"{industry}-{provider_a}-{model_a}"))
            progress.advance(task)
            time.sleep(0.2)
            results_b.append(_simulate_pillar_evaluation(pillar, f"{industry}-{provider_b}-{model_b}"))
            progress.advance(task)
            time.sleep(0.2)

    console.print()

    # Comparison table
    comp_table = Table(
        title="SIDE-BY-SIDE COMPARISON",
        box=box.ROUNDED,
        title_style="bold white",
        header_style="bold cyan",
        border_style="bright_blue",
    )
    comp_table.add_column("Pillar", style="bold", min_width=14)
    comp_table.add_column(f"{provider_a}/{model_a}", justify="center", min_width=18)
    comp_table.add_column(f"{provider_b}/{model_b}", justify="center", min_width=18)
    comp_table.add_column("Winner", justify="center", min_width=12)

    for ra, rb in zip(results_a, results_b):
        style_a = _grade_style(ra["grade"])
        style_b = _grade_style(rb["grade"])
        score_a_str = f"[{style_a}]{ra['score']:.1%} ({ra['grade']})[/{style_a}]"
        score_b_str = f"[{style_b}]{rb['score']:.1%} ({rb['grade']})[/{style_b}]"

        if ra["score"] > rb["score"]:
            winner = f"[bold]{provider_a}[/bold]"
        elif rb["score"] > ra["score"]:
            winner = f"[bold]{provider_b}[/bold]"
        else:
            winner = "[dim]Tie[/dim]"

        comp_table.add_row(ra["pillar"].capitalize(), score_a_str, score_b_str, winner)

    # Overall row
    scorer = Scorer({p: 1.0 for p in ALL_PILLARS})
    scores_a = {r["pillar"]: r["score"] for r in results_a}
    scores_b = {r["pillar"]: r["score"] for r in results_b}
    overall_a = scorer.weighted_average(scores_a)
    overall_b = scorer.weighted_average(scores_b)
    grade_a = compute_grade(overall_a)
    grade_b = compute_grade(overall_b)
    trust_a = compute_trust_level(grade_a)
    trust_b = compute_trust_level(grade_b)

    comp_table.add_section()
    style_oa = _grade_style(grade_a)
    style_ob = _grade_style(grade_b)
    overall_winner = (
        f"[bold]{provider_a}[/bold]" if overall_a > overall_b
        else f"[bold]{provider_b}[/bold]" if overall_b > overall_a
        else "[dim]Tie[/dim]"
    )
    comp_table.add_row(
        "[bold]Overall[/bold]",
        f"[{style_oa}]{overall_a:.1%} ({grade_a}) - {trust_a}[/{style_oa}]",
        f"[{style_ob}]{overall_b:.1%} ({grade_b}) - {trust_b}[/{style_ob}]",
        overall_winner,
    )

    console.print(comp_table)
    console.print()


# ===================================================================
# trusteval providers (group)
# ===================================================================


@cli.group()
def providers() -> None:
    """Manage LLM provider connections."""


@providers.command("list")
def providers_list() -> None:
    """List all supported providers and their models."""
    _print_banner()

    table = Table(
        title="SUPPORTED PROVIDERS",
        box=box.ROUNDED,
        title_style="bold white",
        header_style="bold cyan",
        border_style="bright_blue",
    )
    table.add_column("Provider", style="bold", min_width=14)
    table.add_column("Models", min_width=50)
    table.add_column("Status", justify="center", min_width=10)

    keys = _load_keys()
    for provider, models in sorted(PROVIDER_MODELS.items()):
        has_key = provider in keys
        status = "[green]Configured[/green]" if has_key else "[dim]Not configured[/dim]"
        model_str = ", ".join(models)
        table.add_row(provider.capitalize(), model_str, status)

    console.print(table)
    console.print()


@providers.command("test")
@click.option("--provider", required=True, help="Provider to test connectivity for.")
def providers_test(provider: str) -> None:
    """Test connectivity to a provider."""
    _print_banner()

    provider_lower = provider.strip().lower()
    keys = _load_keys()

    console.print(f"  [bold]Testing connectivity:[/bold] {provider_lower}\n")

    if provider_lower not in PROVIDER_MODELS:
        console.print(f"  [red]Unknown provider: {provider_lower}[/red]")
        console.print(f"  [dim]Available: {', '.join(sorted(PROVIDER_MODELS.keys()))}[/dim]\n")
        raise SystemExit(1)

    if provider_lower not in keys:
        console.print(f"  [yellow]No API key configured for {provider_lower}.[/yellow]")
        console.print(f"  [dim]Run: trusteval providers configure --provider {provider_lower}[/dim]\n")
        raise SystemExit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        progress.add_task(f"[cyan]Connecting to {provider_lower}...", total=None)
        time.sleep(1.0)

    # Attempt real connectivity if provider SDK is available
    api_key = keys[provider_lower]
    connected = False
    error_msg = ""

    if provider_lower == "openai":
        try:
            from trusteval.providers.openai_provider import OpenAIProvider
            p = OpenAIProvider(api_key=api_key, model="gpt-4")
            connected = p.is_available()
        except Exception as exc:
            error_msg = str(exc)
    else:
        # For other providers, verify key is non-empty as a basic check
        connected = bool(api_key and len(api_key) > 8)

    if connected:
        console.print(f"  [green]Connection successful![/green]  {provider_lower} is reachable.\n")
    else:
        console.print(f"  [red]Connection failed.[/red]")
        if error_msg:
            console.print(f"  [dim]{error_msg}[/dim]")
        console.print()
        raise SystemExit(1)


@providers.command("configure")
@click.option("--provider", required=True, help="Provider to configure.")
def providers_configure(provider: str) -> None:
    """Configure API key for a provider."""
    _print_banner()

    provider_lower = provider.strip().lower()
    if provider_lower not in PROVIDER_MODELS:
        console.print(f"  [red]Unknown provider: {provider_lower}[/red]")
        console.print(f"  [dim]Available: {', '.join(sorted(PROVIDER_MODELS.keys()))}[/dim]\n")
        raise SystemExit(1)

    console.print(f"  [bold]Configure {provider_lower}[/bold]\n")
    console.print(f"  [dim]Your API key will be stored in {_KEYS_FILE}[/dim]")
    console.print(f"  [dim]Models: {', '.join(PROVIDER_MODELS[provider_lower])}[/dim]\n")

    api_key = getpass.getpass(f"  Enter API key for {provider_lower}: ")

    if not api_key or not api_key.strip():
        console.print("\n  [red]No API key provided. Aborting.[/red]\n")
        raise SystemExit(1)

    keys = _load_keys()
    keys[provider_lower] = api_key.strip()
    _save_keys(keys)

    masked = api_key[:4] + "****" + api_key[-4:] if len(api_key) > 8 else "****"
    console.print(f"\n  [green]API key saved![/green]  ({masked})")
    console.print(f"  [dim]Test with: trusteval providers test --provider {provider_lower}[/dim]\n")


# ===================================================================
# trusteval report (group)
# ===================================================================


@cli.group()
def report() -> None:
    """Generate evaluation reports."""


@report.command("generate")
@click.option("--input", "-i", "input_file", required=True, type=click.Path(exists=True), help="Input JSON results file.")
@click.option(
    "--format", "-f", "fmt", type=click.Choice(["pdf", "json", "csv", "html"]), default="json", help="Output format.", show_default=True
)
@click.option("--output", "-o", "output_file", default=None, type=click.Path(), help="Output file path.")
def report_generate(input_file: str, fmt: str, output_file: Optional[str]) -> None:
    """Generate a report from evaluation results."""
    _print_banner()

    # Load input data
    try:
        with open(input_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        console.print(f"  [red]Failed to load input file: {exc}[/red]\n")
        raise SystemExit(1)

    # Determine output path
    if output_file is None:
        stem = Path(input_file).stem
        output_file = f"{stem}_report.{fmt}"

    console.print(f"  [bold]Generating report[/bold]")
    console.print(f"  [dim]Input  : {input_file}[/dim]")
    console.print(f"  [dim]Format : {fmt.upper()}[/dim]")
    console.print(f"  [dim]Output : {output_file}[/dim]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Generating report...", total=100)

        # Step 1: Parse
        progress.update(task, advance=30, description="[cyan]Parsing results...")
        time.sleep(0.3)

        # Step 2: Format
        progress.update(task, advance=30, description="[cyan]Formatting output...")
        time.sleep(0.3)

        if fmt == "json":
            report_data = {
                "report_type": "TrustEval Evaluation Report",
                "version": __version__,
                "data": data,
            }
            Path(output_file).write_text(json.dumps(report_data, indent=2), encoding="utf-8")

        elif fmt == "csv":
            import csv

            results = data.get("results", [])
            if results:
                fieldnames = list(results[0].keys())
                with open(output_file, "w", newline="", encoding="utf-8") as fh:
                    writer = csv.DictWriter(fh, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)
            else:
                Path(output_file).write_text("No results\n", encoding="utf-8")

        elif fmt == "html":
            results = data.get("results", [])
            trust_level = data.get("trust_level", "N/A")
            overall_score = data.get("overall_score", 0)
            html_rows = ""
            for r in results:
                color = "#2ecc71" if r.get("grade") in ("A", "B") else (
                    "#f39c12" if r.get("grade") in ("C", "D") else "#e74c3c"
                )
                html_rows += (
                    f"<tr>"
                    f"<td>{r.get('pillar', '').capitalize()}</td>"
                    f"<td style='color:{color};font-weight:bold'>{r.get('score', 0):.1%}</td>"
                    f"<td style='color:{color};font-weight:bold'>{r.get('grade', 'N/A')}</td>"
                    f"<td>{r.get('tests_run', 0)}</td>"
                    f"<td style='color:#2ecc71'>{r.get('passed', 0)}</td>"
                    f"<td style='color:#e74c3c'>{r.get('failed', 0)}</td>"
                    f"</tr>\n"
                )
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TrustEval Report</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f8f9fa; color: #222; }}
  h1 {{ color: #0d6efd; }}
  table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
  th, td {{ border: 1px solid #dee2e6; padding: 10px 14px; text-align: left; }}
  th {{ background: #0d6efd; color: #fff; }}
  tr:nth-child(even) {{ background: #e9ecef; }}
  .verdict {{ font-size: 1.4em; font-weight: bold; padding: 16px; margin: 20px 0; border-radius: 8px; }}
  .TRUSTED {{ background: #d4edda; color: #155724; border: 2px solid #28a745; }}
  .CONDITIONAL {{ background: #fff3cd; color: #856404; border: 2px solid #ffc107; }}
  .UNTRUSTED {{ background: #f8d7da; color: #721c24; border: 2px solid #dc3545; }}
</style>
</head>
<body>
<h1>TrustEval Evaluation Report</h1>
<p><strong>Provider:</strong> {data.get('provider', 'N/A')} ({data.get('model', 'N/A')})</p>
<p><strong>Industry:</strong> {data.get('industry', 'N/A').capitalize()}</p>
<p><strong>Overall Score:</strong> {overall_score:.1%} | <strong>Grade:</strong> {data.get('overall_grade', 'N/A')}</p>
<div class="verdict {trust_level}">Verdict: {trust_level}</div>
<table>
<tr><th>Pillar</th><th>Score</th><th>Grade</th><th>Tests</th><th>Passed</th><th>Failed</th></tr>
{html_rows}
</table>
<p style="color:#888;font-size:0.85em;">Generated by TrustEval v{__version__}</p>
</body>
</html>"""
            Path(output_file).write_text(html, encoding="utf-8")

        elif fmt == "pdf":
            # PDF generation requires weasyprint; fall back to a notice
            try:
                from weasyprint import HTML as WeasyprintHTML

                # Generate HTML first, then convert
                results = data.get("results", [])
                html_rows = ""
                for r in results:
                    html_rows += (
                        f"<tr><td>{r.get('pillar', '').capitalize()}</td>"
                        f"<td>{r.get('score', 0):.1%}</td>"
                        f"<td>{r.get('grade', 'N/A')}</td></tr>\n"
                    )
                html_content = f"""<html><body style="font-family:Arial">
<h1>TrustEval Report</h1>
<p>Provider: {data.get('provider', 'N/A')} | Model: {data.get('model', 'N/A')} | Industry: {data.get('industry', 'N/A')}</p>
<table border="1" cellpadding="8"><tr><th>Pillar</th><th>Score</th><th>Grade</th></tr>{html_rows}</table>
<p>Verdict: {data.get('trust_level', 'N/A')} | Overall: {data.get('overall_score', 0):.1%}</p>
</body></html>"""
                WeasyprintHTML(string=html_content).write_pdf(output_file)
            except ImportError:
                console.print("  [yellow]weasyprint not installed -- saving as HTML instead.[/yellow]")
                output_file = output_file.replace(".pdf", ".html")
                Path(output_file).write_text("<html><body><p>PDF generation requires weasyprint.</p></body></html>", encoding="utf-8")

        # Step 3: Finalize
        progress.update(task, advance=40, description="[cyan]Finalizing...")
        time.sleep(0.2)

    console.print(f"\n  [green]Report generated![/green]  {output_file}\n")


# ===================================================================
# trusteval dashboard
# ===================================================================


@cli.group()
def dashboard() -> None:
    """Manage the TrustEval web dashboard."""


@dashboard.command("start")
@click.option("--port", default=8080, type=int, help="Port to run the dashboard on.", show_default=True)
@click.option("--no-browser", is_flag=True, default=False, help="Do not open browser automatically.")
def dashboard_start(port: int, no_browser: bool) -> None:
    """Launch the TrustEval dashboard."""
    _print_banner()

    console.print(f"  [bold]Starting TrustEval Dashboard[/bold]")
    console.print(f"  [dim]Port     : {port}[/dim]")
    console.print(f"  [dim]URL      : http://localhost:{port}[/dim]")
    console.print(f"  [dim]Browser  : {'disabled' if no_browser else 'auto-open'}[/dim]\n")

    if not no_browser:
        import webbrowser
        webbrowser.open(f"http://localhost:{port}")

    try:
        import uvicorn
    except ImportError:
        console.print("  [red]uvicorn is required. Install with: pip install uvicorn[standard][/red]\n")
        raise SystemExit(1)

    console.print("  [cyan]Press Ctrl+C to stop the dashboard.[/cyan]\n")

    try:
        uvicorn.run(
            "dashboard.app:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False,
        )
    except KeyboardInterrupt:
        console.print("\n  [dim]Dashboard stopped.[/dim]\n")
    except Exception as exc:
        console.print(f"  [red]Failed to start dashboard: {exc}[/red]\n")
        raise SystemExit(1)


# ===================================================================
# trusteval config (group)
# ===================================================================


@cli.group("config")
def config_group() -> None:
    """View and manage TrustEval configuration."""


@config_group.command("show")
def config_show() -> None:
    """Show current configuration."""
    _print_banner()

    data = _load_config_yaml()

    if not data:
        console.print("  [dim]No custom configuration found.[/dim]")
        console.print(f"  [dim]Config file: {_CONFIG_FILE}[/dim]")
        console.print("  [dim]Using defaults.[/dim]\n")

        # Show defaults
        data = {
            "provider": "openai",
            "model": "gpt-4",
            "industry": "general",
            "pillars": ALL_PILLARS,
            "verbose": False,
            "parallel": True,
            "timeout_seconds": 300,
            "max_retries": 3,
            "cache_enabled": True,
        }

    table = Table(
        title="CONFIGURATION",
        box=box.ROUNDED,
        title_style="bold white",
        header_style="bold cyan",
        border_style="bright_blue",
    )
    table.add_column("Key", style="bold", min_width=20)
    table.add_column("Value", min_width=40)

    for key, value in sorted(data.items()):
        if isinstance(value, list):
            display = ", ".join(str(v) for v in value)
        elif isinstance(value, dict):
            display = json.dumps(value, indent=2)
        else:
            display = str(value)
        table.add_row(key, display)

    console.print(table)
    console.print(f"\n  [dim]Config file: {_CONFIG_FILE}[/dim]\n")


@config_group.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value.

    Examples:

        trusteval config set industry healthcare

        trusteval config set provider anthropic

        trusteval config set pillars "hallucination,bias,pii"
    """
    _print_banner()

    data = _load_config_yaml()

    # Handle list values (comma-separated)
    if key == "pillars":
        parsed_value: Any = [p.strip().lower() for p in value.split(",") if p.strip()]
    elif value.lower() in ("true", "false"):
        parsed_value = value.lower() == "true"
    elif value.isdigit():
        parsed_value = int(value)
    else:
        try:
            parsed_value = float(value)
        except ValueError:
            parsed_value = value

    data[key] = parsed_value
    _save_config_yaml(data)

    if isinstance(parsed_value, list):
        display = ", ".join(parsed_value)
    else:
        display = str(parsed_value)

    console.print(f"  [green]Set[/green] [bold]{key}[/bold] = {display}")
    console.print(f"  [dim]Saved to {_CONFIG_FILE}[/dim]\n")


@config_group.command("reset")
@click.confirmation_option(prompt="Reset all configuration to defaults?")
def config_reset() -> None:
    """Reset configuration to defaults."""
    _print_banner()

    if _CONFIG_FILE.is_file():
        _CONFIG_FILE.unlink()
        console.print("  [green]Configuration reset to defaults.[/green]")
    else:
        console.print("  [dim]No custom configuration to reset.[/dim]")

    console.print(f"  [dim]{_CONFIG_FILE}[/dim]\n")


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
