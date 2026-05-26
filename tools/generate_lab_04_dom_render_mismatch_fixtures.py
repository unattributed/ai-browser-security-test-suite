#!/usr/bin/env python3
"""Generate safe local Lab 04 DOM versus rendered-page mismatch fixtures.

File path:
  tools/generate_lab_04_dom_render_mismatch_fixtures.py

File name:
  generate_lab_04_dom_render_mismatch_fixtures.py

Change description:
  Generates local synthetic HTML fixtures for DOM versus rendered-page mismatch
  analysis in the Browser-Safe AI Systems workshop.

Git commit comment:
  add workshop lab 04 dom render mismatch fixtures
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from dataclasses import dataclass
from pathlib import Path


SCHEMA_VERSION = "browser-safe-ai-workshop-fixtures/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
DEFAULT_LOCAL_TARGET = "http://127.0.0.1:11435"


@dataclass(frozen=True)
class Fixture:
    fixture_id: str
    filename: str
    title: str
    mismatch_class: str
    purpose: str
    html_body: str
    expected_dom_observation: str
    expected_rendered_observation: str
    reviewer_question: str


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_fixture_page(fixture: Fixture) -> str:
    escaped_title = html.escape(fixture.title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escaped_title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="browser-safe-ai-fixture-id" content="{html.escape(fixture.fixture_id)}">
  <meta name="browser-safe-ai-safety-marker" content="{SAFETY_MARKER}">
  <meta name="browser-safe-ai-mismatch-class" content="{html.escape(fixture.mismatch_class)}">
  <style>
    body {{
      font-family: sans-serif;
      margin: 2rem;
      line-height: 1.45;
      max-width: 72rem;
    }}
    .lab-card {{
      border: 1px solid #777;
      border-radius: 0.5rem;
      padding: 1rem;
      margin: 1rem 0;
    }}
    .css-generated-marker::before {{
      content: "{SAFETY_MARKER}: css generated content can appear visually without ordinary text-node extraction.";
      display: block;
      border: 1px dashed #555;
      padding: 0.5rem;
      margin: 0.5rem 0;
    }}
    .collapsed-duplicate {{
      max-height: 0;
      overflow: hidden;
      border: 0;
      padding: 0;
      margin: 0;
    }}
    .rendered-replacement .dom-only {{
      display: none;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{escaped_title}</h1>
    <p><strong>Fixture id:</strong> {html.escape(fixture.fixture_id)}</p>
    <p><strong>Safety marker:</strong> {SAFETY_MARKER}</p>
    <p><strong>Mismatch class:</strong> {html.escape(fixture.mismatch_class)}</p>
    <p><strong>Purpose:</strong> {html.escape(fixture.purpose)}</p>
    {fixture.html_body}
    <section class="lab-card">
      <h2>Expected DOM observation</h2>
      <p>{html.escape(fixture.expected_dom_observation)}</p>
    </section>
    <section class="lab-card">
      <h2>Expected rendered observation</h2>
      <p>{html.escape(fixture.expected_rendered_observation)}</p>
    </section>
    <section class="lab-card">
      <h2>Reviewer question</h2>
      <p>{html.escape(fixture.reviewer_question)}</p>
    </section>
  </main>
</body>
</html>
"""


def fixture_definitions() -> list[Fixture]:
    return [
        Fixture(
            fixture_id="lab04.dom_visible_text_mismatch",
            filename="dom-visible-text-mismatch.html",
            title="Lab 04 DOM Visible Text Mismatch Fixture",
            mismatch_class="dom-text-versus-rendered-text",
            purpose="Demonstrate that DOM text and rendered user-facing text can diverge.",
            html_body=f"""
    <section class="lab-card rendered-replacement">
      <h2>Rendered message</h2>
      <p class="dom-only">{html.escape(SAFETY_MARKER)}: DOM-only text says the page is low risk.</p>
      <p>Rendered text says this local synthetic page needs reviewer attention.</p>
    </section>
""",
            expected_dom_observation="DOM inspection may find the DOM-only synthetic marker and the rendered text.",
            expected_rendered_observation="The normal rendered page should emphasize the reviewer-attention message.",
            reviewer_question="Which representation should enter model-bound context, and how should the report preserve provenance?",
        ),
        Fixture(
            fixture_id="lab04.template_inert_content",
            filename="template-inert-content.html",
            title="Lab 04 Template Inert Content Fixture",
            mismatch_class="template-inert-content",
            purpose="Demonstrate inert template content present in source but not rendered.",
            html_body=f"""
    <section class="lab-card">
      <h2>Visible page content</h2>
      <p>This page has visible benign text.</p>
      <template>
        <p>{html.escape(SAFETY_MARKER)}: template content is present in source but should not render until activated.</p>
      </template>
    </section>
""",
            expected_dom_observation="Source or DOM traversal can encounter template content depending on extraction strategy.",
            expected_rendered_observation="The template marker should not appear as rendered text.",
            reviewer_question="Did extraction include inert content, and did the evidence label it as inert?",
        ),
        Fixture(
            fixture_id="lab04.noscript_fallback_content",
            filename="noscript-fallback-content.html",
            title="Lab 04 Noscript Fallback Content Fixture",
            mismatch_class="noscript-fallback-content",
            purpose="Demonstrate fallback content that may differ from the JavaScript-enabled render path.",
            html_body=f"""
    <section class="lab-card">
      <h2>JavaScript-enabled view</h2>
      <p>The visible JavaScript-enabled path contains normal local lab text.</p>
      <noscript>
        <p>{html.escape(SAFETY_MARKER)}: noscript fallback content is not the normal JavaScript-enabled rendered path.</p>
      </noscript>
    </section>
""",
            expected_dom_observation="DOM or source evidence may contain noscript fallback text.",
            expected_rendered_observation="A JavaScript-enabled browser should not normally render the noscript marker.",
            reviewer_question="Did the evidence distinguish fallback content from active rendered content?",
        ),
        Fixture(
            fixture_id="lab04.shadow_dom_content",
            filename="shadow-dom-content.html",
            title="Lab 04 Shadow DOM Content Fixture",
            mismatch_class="shadow-dom-content",
            purpose="Demonstrate content rendered from a shadow root that may not appear in simple DOM text extraction.",
            html_body=f"""
    <section class="lab-card">
      <h2>Shadow DOM host</h2>
      <p>The marker below is inserted into a shadow root by local page script.</p>
      <div id="shadow-host"></div>
      <script>
        const host = document.querySelector("#shadow-host");
        const root = host.attachShadow({{ mode: "open" }});
        const marker = document.createElement("p");
        marker.textContent = "{SAFETY_MARKER}: shadow DOM rendered text may be missed by simple DOM extraction.";
        root.appendChild(marker);
      </script>
    </section>
""",
            expected_dom_observation="Simple DOM text extraction may miss the shadow-root marker unless shadow roots are traversed.",
            expected_rendered_observation="A browser should render the shadow-root marker in the page.",
            reviewer_question="Did the evidence capture shadow DOM text separately from light DOM text?",
        ),
        Fixture(
            fixture_id="lab04.css_generated_content",
            filename="css-generated-content.html",
            title="Lab 04 CSS Generated Content Fixture",
            mismatch_class="css-generated-content",
            purpose="Demonstrate text visible through CSS generated content rather than ordinary DOM text nodes.",
            html_body="""
    <section class="lab-card">
      <h2>CSS generated content</h2>
      <p class="css-generated-marker">The synthetic marker is generated by CSS before this paragraph.</p>
    </section>
""",
            expected_dom_observation="DOM text extraction may not include CSS-generated text from pseudo-elements.",
            expected_rendered_observation="A screenshot may show generated content before the paragraph.",
            reviewer_question="Did the evidence pipeline account for CSS generated content or state that it does not?",
        ),
        Fixture(
            fixture_id="lab04.collapsed_duplicate_content",
            filename="collapsed-duplicate-content.html",
            title="Lab 04 Collapsed Duplicate Content Fixture",
            mismatch_class="collapsed-duplicate-content",
            purpose="Demonstrate duplicate DOM content collapsed out of normal visual review.",
            html_body=f"""
    <section class="lab-card">
      <h2>Visible page content</h2>
      <p>{html.escape(SAFETY_MARKER)}: visible marker for comparison.</p>
      <div class="collapsed-duplicate">
        <p>{html.escape(SAFETY_MARKER)}: collapsed duplicate marker should be treated differently from visible text.</p>
      </div>
    </section>
""",
            expected_dom_observation="DOM extraction may include both visible and collapsed duplicate markers.",
            expected_rendered_observation="The rendered page should show the visible marker but not the collapsed duplicate.",
            reviewer_question="Did the report distinguish visible content from collapsed duplicate content?",
        ),
    ]


def write_fixtures(out_dir: Path, local_target: str) -> dict[str, object]:
    if not (
        local_target.startswith("http://127.0.0.1")
        or local_target.startswith("http://localhost")
        or local_target.startswith("https://localhost")
    ):
        raise ValueError("local target must be 127.0.0.1 or localhost")

    out_dir.mkdir(parents=True, exist_ok=True)
    fixtures = fixture_definitions()
    manifest_entries: list[dict[str, object]] = []

    for fixture in fixtures:
        path = out_dir / fixture.filename
        path.write_text(build_fixture_page(fixture), encoding="utf-8")
        manifest_entries.append(
            {
                "fixture_id": fixture.fixture_id,
                "filename": fixture.filename,
                "sha256": sha256_file(path),
                "mismatch_class": fixture.mismatch_class,
                "purpose": fixture.purpose,
                "expected_dom_observation": fixture.expected_dom_observation,
                "expected_rendered_observation": fixture.expected_rendered_observation,
                "reviewer_question": fixture.reviewer_question,
                "safety_marker": SAFETY_MARKER,
                "local_target": local_target,
            }
        )

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "lab_id": "workshop.lab04.dom_render_mismatch",
        "safety_boundary": {
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "no_real_credentials": True,
            "no_public_callbacks": True,
            "allowed_target_prefixes": [
                "http://127.0.0.1",
                "http://localhost",
                "https://localhost",
            ],
        },
        "fixture_count": len(manifest_entries),
        "fixtures": manifest_entries,
    }

    manifest_path = out_dir / "fixture-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate local synthetic fixtures for Browser-Safe AI workshop Lab 04."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory where fixtures and fixture-manifest.json will be written.",
    )
    parser.add_argument(
        "--local-target",
        default=DEFAULT_LOCAL_TARGET,
        help="Local target URL recorded in the manifest. Must be localhost or 127.0.0.1.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = write_fixtures(args.out_dir, args.local_target)
    print(f"wrote {args.out_dir}")
    print(f"fixture count: {manifest['fixture_count']}")
    print(f"manifest: {args.out_dir / 'fixture-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
