from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB06_DOC = ROOT / "docs/workshop/labs/06-iframe-and-frame-tree-source-confusion.md"
HELPER = ROOT / "tools/run_iframe_frame_tree_lab.py"
LIVE_RUNNER = ROOT / "tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py"
WORKSHOP_VALIDATOR = ROOT / "tools/validate_workshop_labs.py"
PRACTICAL_VALIDATOR = ROOT / "tools/validate_workshop_practical_labs.py"

REQUIRED_HEADINGS = [
    "## Method being taught",
    "## Real-world behavior being emulated",
    "## Local-only PoC payload or controlled test input",
    "## Step-by-step execution",
    "## Required student-authored variation",
    "## Evidence to collect",
    "## Expected failure modes",
    "## Defender interpretation",
    "## Reportable finding",
    "## Safety and authorization boundary"
]

LAB06_VARIANTS = [
    "baseline",
    "sandboxed_frame",
    "srcdoc_hidden_context",
    "nested_frame_chain"
]

REQUIRED_TERMS = [
    "iframe and frame-tree source confusion",
    "tools/run_iframe_frame_tree_lab.py",
    "tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py",
    "one-command lab 06 iframe frame-tree end-to-end live evidence runner",
    "weak target startup sop",
    "browser source",
    "dom",
    "visible text",
    "screenshot evidence",
    "frame-tree.json",
    "frame-url-list.txt",
    "top-page-dom-snapshot.html",
    "frame-dom-snapshots/index.json",
    "sandbox-findings.json",
    "srcdoc-findings.json",
    "cross-frame-rendered-text.txt",
    "model-bound-context.txt",
    "direct local http responses with proxied local http responses",
    "artifact-manifest.json",
    "sha256sums.txt",
    "synthetic-lab-marker",
    "student-authored variation",
    "mitmproxy ca private material",
    "intentionally weak target must remain vulnerable",
    "no production security validation claim",
]

SAFETY_TERMS = [
    "provided local weak target",
    "synthetic data",
    "leave the intentionally weak target unchanged",
    "real credentials",
    "real customer data",
    "third-party systems",
    "nvidia drivers",
]


def read_lab06() -> str:
    return LAB06_DOC.read_text(encoding="utf-8")


def test_lab06_canonical_assets_exist() -> None:
    assert LAB06_DOC.exists()
    assert HELPER.exists()
    assert LIVE_RUNNER.exists()
    assert WORKSHOP_VALIDATOR.exists()
    assert PRACTICAL_VALIDATOR.exists()


def test_lab06_contains_required_instructional_alignment_headings() -> None:
    text = read_lab06()
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in text]
    assert missing == []


def test_lab06_contains_required_courseware_terms_case_insensitive() -> None:
    lower_text = read_lab06().casefold()
    missing = [term for term in REQUIRED_TERMS if term.casefold() not in lower_text]
    assert missing == []


def test_lab06_defines_student_variation_and_reportable_evidence() -> None:
    text = read_lab06()
    lower_text = text.casefold()
    assert "lab06_variation_frame_provenance_safe_marker" in lower_text
    assert "student must create one local-only variation" in lower_text
    assert "evidence to collect" in lower_text
    assert "reportable finding" in lower_text
    assert "defender recommendation" in lower_text


def test_lab06_defines_all_canonical_variants() -> None:
    text = read_lab06()
    missing = [variant for variant in LAB06_VARIANTS if variant not in text]
    assert missing == []


def test_lab06_defines_multisource_frame_evidence_workflow() -> None:
    lower_text = read_lab06().casefold()
    for term in [
        "browser source",
        "dom",
        "visible text",
        "screenshot evidence",
        "frame tree capture",
        "frame url capture",
        "child-frame dom snapshots",
        "direct and proxied http capture",
        "marker provenance review",
        "model-bound context review",
        "manifest records",
        "checksums",
    ]:
        assert term in lower_text


def test_lab06_proxy_capture_instruction_is_practical_and_local_only() -> None:
    lower_text = read_lab06().casefold()
    assert "practical proxy evidence exercise" in lower_text
    assert "docs/workshop/local-proxy-evidence-workflow.md" in lower_text
    assert "direct local http responses with proxied local http responses" in lower_text
    assert "mitmdump" in lower_text or "mitmproxy" in lower_text
    assert "owasp zap" in lower_text or "zap" in lower_text
    assert "external iframe urls" in lower_text
    assert "public callback" in lower_text


def test_lab06_safety_boundary_preserves_weak_target_and_driver_boundary() -> None:
    lower_text = read_lab06().casefold()
    missing = [term for term in SAFETY_TERMS if term.casefold() not in lower_text]
    assert missing == []
    assert "do not install or modify nvidia drivers" in lower_text
