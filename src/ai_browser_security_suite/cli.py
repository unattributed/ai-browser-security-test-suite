# File: src/ai_browser_security_suite/cli.py
# Change description: CLI for local lab, ollama-webui target validation, authorized recon, capture, and reports.
# Git commit comment: focus suite on ollama webui local target
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ai_browser_security_suite.browser_capture import capture_url
from ai_browser_security_suite.config import ScopeError, load_scope, write_scope_template
from ai_browser_security_suite.local_lab import build_lab, load_cases, serve_lab
from ai_browser_security_suite.recon.blackbox import run_blackbox_recon
from ai_browser_security_suite.report import write_markdown_report
from ai_browser_security_suite.targets.ollama_webui import run_validation_async

console = Console()


def cmd_init_scope(args):
    write_scope_template(args.out)
    console.print(f"wrote scope template: {args.out}")
    return 0


def cmd_case_list(args):
    table = Table(title="Safe browser-AI test cases")
    table.add_column("Case ID")
    table.add_column("Category")
    table.add_column("Supported parts")
    table.add_column("Title")

    for case in load_cases(args.cases):
        table.add_row(case.case_id, case.category, ", ".join(case.supported_parts), case.title)

    console.print(table)
    return 0


def cmd_lab_build(args):
    written = build_lab(args.cases, args.out)
    console.print(f"built {len(written)} pages in {args.out}")
    return 0


def cmd_lab_serve(args):
    serve_lab(args.directory, args.host, args.port)
    return 0


def cmd_recon(args):
    try:
        scope = load_scope(args.scope)
        scope.require_authorization(active_requested=not args.passive_only, authorization_flag=args.i_have_authorization)
        evidence = run_blackbox_recon(scope, args.out, args.passive_only)
        report = write_markdown_report(args.out, "Authorized Black-Box Browser-AI Reconnaissance Report")
    except ScopeError as exc:
        console.print(f"[red]scope error:[/red] {exc}")
        return 2

    console.print(f"wrote evidence: {evidence}")
    console.print(f"wrote report: {report}")
    return 0


def cmd_capture(args):
    try:
        scope = load_scope(args.scope) if args.scope else None
        if scope:
            scope.require_authorization(active_requested=True, authorization_flag=args.i_have_authorization)
        record = capture_url(args.url, args.out, scope)
        report = write_markdown_report(args.out, "Browser Evidence Capture Report")
    except ScopeError as exc:
        console.print(f"[red]scope error:[/red] {exc}")
        return 2

    console.print(record.to_json())
    console.print(f"wrote report: {report}")
    return 0


def cmd_report(args):
    console.print(f"wrote report: {write_markdown_report(args.evidence_dir, args.title)}")
    return 0


def cmd_ollama_validate(args):
    if not args.i_have_authorization:
        console.print(
            "[red]authorization required:[/red] use --i-have-authorization only when testing "
            "your local ollama-webui instance or an explicitly authorized target."
        )
        return 2

    return asyncio.run(
        run_validation_async(
            base_url=args.base_url,
            model=args.model,
            cases_path=Path(args.cases),
            out_dir=Path(args.out),
            response_timeout_ms=args.response_timeout_ms,
        )
    )


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ai-browser-suite",
        description=(
            "Blue-team validation for browser-based AI ecosystems. "
            "The supported public target is the local unattributed/ollama-webui application."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    command = sub.add_parser("init-scope")
    command.add_argument("--out", default="examples/client-scope.local.yaml")
    command.set_defaults(func=cmd_init_scope)

    command = sub.add_parser("case-list")
    command.add_argument("--cases", default="payloads/safe_browser_ai_cases.yaml")
    command.set_defaults(func=cmd_case_list)

    command = sub.add_parser("lab-build")
    command.add_argument("--cases", default="payloads/safe_browser_ai_cases.yaml")
    command.add_argument("--out", default="local_lab")
    command.set_defaults(func=cmd_lab_build)

    command = sub.add_parser("lab-serve")
    command.add_argument("--directory", default="local_lab")
    command.add_argument("--host", default="127.0.0.1")
    command.add_argument("--port", type=int, default=8088)
    command.set_defaults(func=cmd_lab_serve)

    command = sub.add_parser("recon")
    command.add_argument("--scope", required=True)
    command.add_argument("--out", default="reports/recon")
    command.add_argument("--passive-only", action="store_true")
    command.add_argument("--i-have-authorization", action="store_true")
    command.set_defaults(func=cmd_recon)

    command = sub.add_parser("capture")
    command.add_argument("--url", required=True)
    command.add_argument("--out", default="reports/browser-capture")
    command.add_argument("--scope")
    command.add_argument("--i-have-authorization", action="store_true")
    command.set_defaults(func=cmd_capture)

    command = sub.add_parser("report")
    command.add_argument("--evidence-dir", required=True)
    command.add_argument("--title", default="AI Browser Security Evidence Report")
    command.set_defaults(func=cmd_report)

    command = sub.add_parser("ollama-validate")
    command.add_argument("--base-url", default="http://127.0.0.1:11435/")
    command.add_argument("--model", default=None)
    command.add_argument("--cases", default="payloads/ollama_webui_safe_prompts.yaml")
    command.add_argument("--out", default="reports/ollama-webui-validation")
    command.add_argument("--response-timeout-ms", type=int, default=180000)
    command.add_argument("--i-have-authorization", action="store_true")
    command.set_defaults(func=cmd_ollama_validate)

    return parser


def main():
    args = build_parser().parse_args()
    raise SystemExit(args.func(args))
