from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re
from typing import Any, Mapping, Protocol
from urllib.parse import urljoin, urlparse

from ai_browser_security_suite.evidence import EvidenceRecord, EvidenceWriter, sha256_file

IFRAME_FRAME_TREE_LAB_ID = "guided.iframe_frame_tree_evidence"
IFRAME_FRAME_TREE_TARGET_SCENARIO_ID = "browser.iframe_frame_tree"
IFRAME_FRAME_TREE_SUPPORTED_PARTS = ["Part 12", "Part 24", "Part 26", "Part 31"]
IFRAME_FRAME_TREE_VARIANTS = ("baseline", "sandboxed_frame", "srcdoc_hidden_context", "nested_frame_chain")
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
MAX_CAPTURED_TEXT_CHARS = 200_000
MAX_FRAME_DOM_CHARS = 200_000
MAX_FRAME_COUNT = 16
EXPECTED_LAB_HEADER = "X-Browser-Safe-Lab"
EXPECTED_SCENARIO_HEADER = "X-Browser-Safe-Scenario"
EXPECTED_VARIANT_HEADER = "X-Browser-Safe-Variant"


class IframeFrameTreeError(RuntimeError):
    """Raised when iframe/frame-tree evidence capture leaves the local lab boundary or fails."""


@dataclass(frozen=True)
class FrameNodeEvidence:
    """One observed browser frame and its bounded DOM/rendered evidence."""

    frame_key: str
    parent_frame_key: str | None
    depth: int
    name: str
    url: str
    title_text: str
    dom_snapshot_html: str
    rendered_text: str
    child_frame_keys: tuple[str, ...]

    @property
    def is_top_frame(self) -> bool:
        return self.parent_frame_key is None

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "frame_key": self.frame_key,
            "parent_frame_key": self.parent_frame_key,
            "depth": self.depth,
            "name": self.name,
            "url": self.url,
            "title_text": self.title_text,
            "child_frame_keys": list(self.child_frame_keys),
            "rendered_text_excerpt": self.rendered_text[:1000],
            "dom_snapshot_size_chars": len(self.dom_snapshot_html),
            "rendered_text_size_chars": len(self.rendered_text),
        }


@dataclass(frozen=True)
class SandboxFinding:
    """One iframe sandbox attribute observed from browser-rendered DOM."""

    parent_frame_key: str
    iframe_selector: str
    iframe_id: str
    iframe_name: str
    iframe_title: str
    sandbox: str
    src: str
    srcdoc_present: bool
    data_role: str | None = None


@dataclass(frozen=True)
class SrcdocFinding:
    """One srcdoc iframe observed from browser-rendered DOM."""

    parent_frame_key: str
    iframe_selector: str
    iframe_id: str
    iframe_name: str
    iframe_title: str
    srcdoc_excerpt: str
    hidden_marker_present: bool
    data_role: str | None = None


@dataclass(frozen=True)
class BrowserFrameTreeEvidence:
    """Raw frame-tree evidence captured from a browser renderer."""

    url: str
    final_url: str
    status_code: int
    response_headers: Mapping[str, str]
    frames: tuple[FrameNodeEvidence, ...]
    sandbox_findings: tuple[SandboxFinding, ...]
    srcdoc_findings: tuple[SrcdocFinding, ...]
    blocked_external_urls: tuple[str, ...] = ()


@dataclass(frozen=True)
class IframeFrameTreeCapture:
    """Structured iframe/frame-tree evidence suitable for JSON output."""

    lab_id: str
    target_scenario_id: str
    variant: str
    url: str
    final_url: str
    status_code: int
    response_headers: dict[str, str]
    frames: tuple[FrameNodeEvidence, ...]
    sandbox_findings: tuple[SandboxFinding, ...]
    srcdoc_findings: tuple[SrcdocFinding, ...]
    cross_frame_rendered_text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "lab_id": self.lab_id,
            "target_scenario_id": self.target_scenario_id,
            "variant": self.variant,
            "url": self.url,
            "final_url": self.final_url,
            "status_code": self.status_code,
            "response_headers": self.response_headers,
            "frame_count": len(self.frames),
            "frames": [frame.to_summary_dict() for frame in self.frames],
            "sandbox_findings": [asdict(item) for item in self.sandbox_findings],
            "srcdoc_findings": [asdict(item) for item in self.srcdoc_findings],
            "cross_frame_rendered_text_size_chars": len(self.cross_frame_rendered_text),
        }


class FrameTreeRenderer(Protocol):
    """Protocol implemented by Playwright or deterministic test renderers."""

    def capture_frame_tree(self, url: str, *, timeout_seconds: float = 10.0) -> BrowserFrameTreeEvidence:
        """Capture browser frame tree, DOM snapshots, rendered text, sandbox, and srcdoc evidence."""


def normalize_variant(variant: str | None) -> str:
    """Return a supported iframe/frame-tree variant, defaulting safely to baseline."""

    candidate = (variant or "baseline").strip().lower()
    if candidate not in IFRAME_FRAME_TREE_VARIANTS:
        return "baseline"
    return candidate


def _is_loopback_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    return parsed.hostname in LOOPBACK_HOSTS


def _is_allowed_frame_url(url: str) -> bool:
    if _is_loopback_url(url):
        return True
    parsed = urlparse(url)
    return parsed.scheme == "about" and parsed.path in {"blank", "srcdoc"}


def _require_loopback_url(url: str, label: str) -> None:
    if not _is_loopback_url(url):
        raise IframeFrameTreeError(f"{label} must be a loopback URL: {url}")


def _require_allowed_frame_url(url: str, label: str) -> None:
    if not _is_allowed_frame_url(url):
        raise IframeFrameTreeError(f"{label} must be loopback or about:srcdoc/about:blank: {url}")


def iframe_frame_tree_target_url(base_url: str, variant: str = "baseline") -> str:
    """Build the local iframe/frame-tree URL for a supported target."""

    normalized_base = base_url.rstrip("/") + "/"
    normalized_variant = normalize_variant(variant)
    url = urljoin(normalized_base, f"browser-safe/iframe-frame-tree?variant={normalized_variant}")
    _require_loopback_url(url, "iframe/frame-tree target URL")
    return url


def _normalize_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {str(key).lower(): str(value) for key, value in headers.items()}


def _header_value(headers: Mapping[str, str], name: str) -> str | None:
    return _normalize_headers(headers).get(name.lower())


def _truncate_text(value: str, limit: int = MAX_CAPTURED_TEXT_CHARS) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n[truncated by ai-browser-security-suite]\n"


def _safe_snapshot_name(frame: FrameNodeEvidence, index: int) -> str:
    base = frame.frame_key or f"frame-{index}"
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "-", base).strip(".-")
    return f"{index:02d}-{safe or 'frame'}.html"


def _require_target_headers(page: BrowserFrameTreeEvidence, expected_variant: str) -> None:
    lab = _header_value(page.response_headers, EXPECTED_LAB_HEADER)
    scenario = _header_value(page.response_headers, EXPECTED_SCENARIO_HEADER)
    variant = _header_value(page.response_headers, EXPECTED_VARIANT_HEADER)

    if lab != IFRAME_FRAME_TREE_LAB_ID:
        raise IframeFrameTreeError(f"target response missing or wrong {EXPECTED_LAB_HEADER}: {lab!r}")
    if scenario != IFRAME_FRAME_TREE_TARGET_SCENARIO_ID:
        raise IframeFrameTreeError(f"target response missing or wrong {EXPECTED_SCENARIO_HEADER}: {scenario!r}")
    if variant != expected_variant:
        raise IframeFrameTreeError(f"target response missing or wrong {EXPECTED_VARIANT_HEADER}: {variant!r}")


def _frame_depth(parent_key: str | None, frames_by_key: Mapping[str, FrameNodeEvidence]) -> int:
    if parent_key is None:
        return 0
    parent = frames_by_key.get(parent_key)
    if parent is None:
        return 1
    return parent.depth + 1


def _coerce_frame(raw: Mapping[str, Any], index: int) -> FrameNodeEvidence:
    child_frame_keys = raw.get("child_frame_keys") or raw.get("children") or []
    if not isinstance(child_frame_keys, (list, tuple)):
        child_frame_keys = []
    return FrameNodeEvidence(
        frame_key=str(raw.get("frame_key") or raw.get("key") or f"frame-{index}"),
        parent_frame_key=str(raw["parent_frame_key"]) if raw.get("parent_frame_key") is not None else None,
        depth=int(raw.get("depth") or 0),
        name=str(raw.get("name") or ""),
        url=str(raw.get("url") or "about:blank"),
        title_text=str(raw.get("title_text") or raw.get("title") or ""),
        dom_snapshot_html=_truncate_text(str(raw.get("dom_snapshot_html") or raw.get("html") or ""), MAX_FRAME_DOM_CHARS),
        rendered_text=_truncate_text(str(raw.get("rendered_text") or raw.get("text") or "")),
        child_frame_keys=tuple(str(item) for item in child_frame_keys),
    )


def _coerce_sandbox_finding(raw: Mapping[str, Any]) -> SandboxFinding:
    return SandboxFinding(
        parent_frame_key=str(raw.get("parent_frame_key") or "top"),
        iframe_selector=str(raw.get("iframe_selector") or raw.get("selector") or "iframe"),
        iframe_id=str(raw.get("iframe_id") or raw.get("id") or ""),
        iframe_name=str(raw.get("iframe_name") or raw.get("name") or ""),
        iframe_title=str(raw.get("iframe_title") or raw.get("title") or ""),
        sandbox=str(raw.get("sandbox") or ""),
        src=str(raw.get("src") or ""),
        srcdoc_present=bool(raw.get("srcdoc_present") or raw.get("srcdoc")),
        data_role=str(raw.get("data_role")) if raw.get("data_role") is not None else None,
    )


def _coerce_srcdoc_finding(raw: Mapping[str, Any]) -> SrcdocFinding:
    return SrcdocFinding(
        parent_frame_key=str(raw.get("parent_frame_key") or "top"),
        iframe_selector=str(raw.get("iframe_selector") or raw.get("selector") or "iframe"),
        iframe_id=str(raw.get("iframe_id") or raw.get("id") or ""),
        iframe_name=str(raw.get("iframe_name") or raw.get("name") or ""),
        iframe_title=str(raw.get("iframe_title") or raw.get("title") or ""),
        srcdoc_excerpt=str(raw.get("srcdoc_excerpt") or raw.get("srcdoc") or "")[:1000],
        hidden_marker_present=bool(raw.get("hidden_marker_present")),
        data_role=str(raw.get("data_role")) if raw.get("data_role") is not None else None,
    )


def _normalize_frames(items: tuple[FrameNodeEvidence, ...] | list[Any] | tuple[Any, ...]) -> tuple[FrameNodeEvidence, ...]:
    frames: list[FrameNodeEvidence] = []
    for index, item in enumerate(items):
        if isinstance(item, FrameNodeEvidence):
            frames.append(item)
        elif isinstance(item, Mapping):
            frames.append(_coerce_frame(item, index))
    return tuple(frames)


def _normalize_sandbox_findings(items: tuple[SandboxFinding, ...] | list[Any] | tuple[Any, ...]) -> tuple[SandboxFinding, ...]:
    findings: list[SandboxFinding] = []
    for item in items:
        if isinstance(item, SandboxFinding):
            findings.append(item)
        elif isinstance(item, Mapping):
            findings.append(_coerce_sandbox_finding(item))
    return tuple(findings)


def _normalize_srcdoc_findings(items: tuple[SrcdocFinding, ...] | list[Any] | tuple[Any, ...]) -> tuple[SrcdocFinding, ...]:
    findings: list[SrcdocFinding] = []
    for item in items:
        if isinstance(item, SrcdocFinding):
            findings.append(item)
        elif isinstance(item, Mapping):
            findings.append(_coerce_srcdoc_finding(item))
    return tuple(findings)


class PlaywrightFrameTreeRenderer:
    """Playwright-backed renderer for live local iframe/frame-tree capture."""

    def capture_frame_tree(self, url: str, *, timeout_seconds: float = 10.0) -> BrowserFrameTreeEvidence:
        """Capture iframe/frame-tree evidence with Chromium through Playwright."""

        _require_loopback_url(url, "iframe/frame-tree Playwright URL")
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover - dependency is declared, but keep error clear.
            raise IframeFrameTreeError("Playwright is required for live iframe/frame-tree capture") from exc

        timeout_ms = max(1, int(timeout_seconds * 1000))
        observed_external_urls: list[str] = []

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                context = browser.new_context()

                def route_guard(route: Any) -> None:
                    request_url = route.request.url
                    if _is_allowed_frame_url(request_url):
                        route.continue_()
                        return
                    observed_external_urls.append(request_url)
                    route.abort()

                context.route("**/*", route_guard)
                page = context.new_page()
                response = page.goto(url, wait_until="networkidle", timeout=timeout_ms)
                if response is None:
                    raise IframeFrameTreeError(f"Playwright did not receive a response for {url}")
                if observed_external_urls:
                    raise IframeFrameTreeError(
                        "iframe/frame-tree target attempted external URL load: " + ", ".join(observed_external_urls)
                    )

                frames_raw = list(page.frames)
                if len(frames_raw) > MAX_FRAME_COUNT:
                    raise IframeFrameTreeError(f"frame count exceeds MAX_FRAME_COUNT={MAX_FRAME_COUNT}")

                frame_key_by_object = {frame: ("top" if frame == page.main_frame else f"frame-{index}") for index, frame in enumerate(frames_raw)}
                child_keys: dict[str, list[str]] = {key: [] for key in frame_key_by_object.values()}
                for frame in frames_raw:
                    parent = frame.parent_frame
                    if parent is not None and parent in frame_key_by_object:
                        child_keys[frame_key_by_object[parent]].append(frame_key_by_object[frame])

                frames: list[FrameNodeEvidence] = []
                frame_depths: dict[str, int] = {"top": 0}
                for frame in frames_raw:
                    key = frame_key_by_object[frame]
                    parent = frame.parent_frame
                    parent_key = frame_key_by_object.get(parent) if parent is not None else None
                    depth = 0 if parent_key is None else frame_depths.get(parent_key, 0) + 1
                    frame_depths[key] = depth
                    frame_url = frame.url or "about:blank"
                    _require_allowed_frame_url(frame_url, f"frame {key} URL")
                    try:
                        title_text = str(frame.evaluate("() => document.title || ''"))
                    except Exception:
                        title_text = "[title unavailable]"
                    try:
                        dom_snapshot_html = str(frame.content())
                    except Exception as exc:
                        dom_snapshot_html = f"<!-- frame DOM unavailable: {type(exc).__name__} -->"
                    try:
                        rendered_text = str(frame.evaluate("() => document.body ? document.body.innerText : ''"))
                    except Exception as exc:
                        rendered_text = f"[rendered text unavailable: {type(exc).__name__}]"

                    frames.append(
                        FrameNodeEvidence(
                            frame_key=key,
                            parent_frame_key=parent_key,
                            depth=depth,
                            name=frame.name,
                            url=frame_url,
                            title_text=title_text,
                            dom_snapshot_html=_truncate_text(dom_snapshot_html, MAX_FRAME_DOM_CHARS),
                            rendered_text=_truncate_text(rendered_text),
                            child_frame_keys=tuple(child_keys.get(key, [])),
                        )
                    )

                sandbox_raw = page.evaluate(
                    """
                    () => Array.from(document.querySelectorAll('iframe')).map((element, index) => ({
                      parent_frame_key: 'top',
                      iframe_selector: element.id ? `#${element.id}` : `iframe:nth-of-type(${index + 1})`,
                      iframe_id: element.id || '',
                      iframe_name: element.getAttribute('name') || '',
                      iframe_title: element.getAttribute('title') || '',
                      sandbox: element.getAttribute('sandbox') || '',
                      src: element.getAttribute('src') || '',
                      srcdoc_present: element.hasAttribute('srcdoc'),
                      data_role: element.getAttribute('data-browser-safe-frame-role'),
                    })).filter((item) => item.sandbox !== '')
                    """
                )
                srcdoc_raw = page.evaluate(
                    """
                    () => Array.from(document.querySelectorAll('iframe')).map((element, index) => {
                      const srcdoc = element.getAttribute('srcdoc') || '';
                      if (!srcdoc) { return null; }
                      return {
                        parent_frame_key: 'top',
                        iframe_selector: element.id ? `#${element.id}` : `iframe:nth-of-type(${index + 1})`,
                        iframe_id: element.id || '',
                        iframe_name: element.getAttribute('name') || '',
                        iframe_title: element.getAttribute('title') || '',
                        srcdoc_excerpt: srcdoc.slice(0, 1000),
                        hidden_marker_present: srcdoc.includes('Synthetic hidden srcdoc marker'),
                        data_role: element.getAttribute('data-browser-safe-frame-role'),
                      };
                    }).filter(Boolean)
                    """
                )

                return BrowserFrameTreeEvidence(
                    url=url,
                    final_url=page.url,
                    status_code=response.status,
                    response_headers=response.headers,
                    frames=tuple(frames),
                    sandbox_findings=_normalize_sandbox_findings(sandbox_raw or []),
                    srcdoc_findings=_normalize_srcdoc_findings(srcdoc_raw or []),
                    blocked_external_urls=tuple(observed_external_urls),
                )
            finally:
                browser.close()


def _frame_tree_text(frames: tuple[FrameNodeEvidence, ...]) -> str:
    lines: list[str] = []
    for frame in sorted(frames, key=lambda item: (item.depth, item.frame_key)):
        lines.append(f"[{frame.frame_key}] depth={frame.depth} url={frame.url}")
        if frame.rendered_text:
            lines.append(frame.rendered_text)
        lines.append("")
    return _truncate_text("\n".join(lines))


def capture_iframe_frame_tree(
    url: str,
    *,
    variant: str = "baseline",
    timeout_seconds: float = 10.0,
    renderer: FrameTreeRenderer | None = None,
) -> IframeFrameTreeCapture:
    """Capture iframe/frame-tree evidence from the local lab target."""

    normalized_variant = normalize_variant(variant)
    _require_loopback_url(url, "iframe/frame-tree target URL")
    active_renderer = renderer or PlaywrightFrameTreeRenderer()
    page = active_renderer.capture_frame_tree(url, timeout_seconds=timeout_seconds)
    _require_loopback_url(page.final_url, "iframe/frame-tree final URL")
    _require_target_headers(page, normalized_variant)
    if page.status_code >= 400:
        raise IframeFrameTreeError(f"iframe/frame-tree target returned HTTP {page.status_code}")
    if page.blocked_external_urls:
        raise IframeFrameTreeError(
            "iframe/frame-tree target attempted external URL load: " + ", ".join(page.blocked_external_urls)
        )

    frames = _normalize_frames(page.frames)
    if not frames:
        raise IframeFrameTreeError("iframe/frame-tree capture did not return any frames")
    if len(frames) > MAX_FRAME_COUNT:
        raise IframeFrameTreeError(f"frame count exceeds MAX_FRAME_COUNT={MAX_FRAME_COUNT}")

    frame_keys = {frame.frame_key for frame in frames}
    if "top" not in frame_keys:
        raise IframeFrameTreeError("iframe/frame-tree capture must include top frame")
    for frame in frames:
        _require_allowed_frame_url(frame.url, f"frame {frame.frame_key} URL")
        if frame.parent_frame_key is not None and frame.parent_frame_key not in frame_keys:
            raise IframeFrameTreeError(
                f"frame {frame.frame_key} references missing parent frame {frame.parent_frame_key}"
            )
        for child_key in frame.child_frame_keys:
            if child_key not in frame_keys:
                raise IframeFrameTreeError(f"frame {frame.frame_key} references missing child frame {child_key}")

    return IframeFrameTreeCapture(
        lab_id=IFRAME_FRAME_TREE_LAB_ID,
        target_scenario_id=IFRAME_FRAME_TREE_TARGET_SCENARIO_ID,
        variant=normalized_variant,
        url=url,
        final_url=page.final_url,
        status_code=page.status_code,
        response_headers=_normalize_headers(page.response_headers),
        frames=frames,
        sandbox_findings=_normalize_sandbox_findings(page.sandbox_findings),
        srcdoc_findings=_normalize_srcdoc_findings(page.srcdoc_findings),
        cross_frame_rendered_text=_frame_tree_text(frames),
    )


def _model_bound_context(capture: IframeFrameTreeCapture) -> str:
    lines = [
        "Browser-Safe AI Systems iframe/frame-tree lab context",
        "",
        f"Lab ID: {capture.lab_id}",
        f"Target scenario ID: {capture.target_scenario_id}",
        f"Variant: {capture.variant}",
        f"URL: {capture.url}",
        f"Final URL: {capture.final_url}",
        f"HTTP status: {capture.status_code}",
        f"Observed frame count: {len(capture.frames)}",
        "",
        "Frame tree summary:",
    ]
    for frame in sorted(capture.frames, key=lambda item: (item.depth, item.frame_key)):
        parent = frame.parent_frame_key or "none"
        children = ", ".join(frame.child_frame_keys) if frame.child_frame_keys else "none"
        lines.append(f"- frame={frame.frame_key} parent={parent} depth={frame.depth} children={children} url={frame.url}")
    lines.extend(
        [
            "",
            f"Sandbox finding count: {len(capture.sandbox_findings)}",
            f"Srcdoc finding count: {len(capture.srcdoc_findings)}",
            "",
            "Cross-frame rendered text excerpt:",
            capture.cross_frame_rendered_text[:1500],
            "",
            "Instruction to analyst:",
            "Review the browser-observed frame tree, frame URLs, sandbox findings, srcdoc findings, and cross-frame rendered text together.",
            "Do not treat static top-page HTML parsing alone as sufficient evidence for this lab.",
            "Do not treat model output as a deterministic policy decision.",
        ]
    )
    return "\n".join(lines) + "\n"


def _model_response_placeholder(capture: IframeFrameTreeCapture) -> dict[str, Any]:
    return {
        "lab_id": capture.lab_id,
        "target_scenario_id": capture.target_scenario_id,
        "variant": capture.variant,
        "status": "not_submitted_to_model",
        "reason": (
            "The iframe/frame-tree lab captures browser evidence and a model-bound context artifact. "
            "This helper does not submit content to a live model by default."
        ),
    }


def _lab_report(capture: IframeFrameTreeCapture) -> str:
    lines = [
        "# Iframe/frame-tree Evidence Lab Report",
        "",
        "## Scope",
        "",
        "Local-only Browser-Safe AI Systems guided lab evidence for iframe and nested frame-tree behavior.",
        "",
        "## Mapping",
        "",
        f"- Guided lab: `{capture.lab_id}`",
        f"- Target scenario: `{capture.target_scenario_id}`",
        f"- Variant: `{capture.variant}`",
        "- Series parts: " + ", ".join(IFRAME_FRAME_TREE_SUPPORTED_PARTS),
        "",
        "## Required evidence standard",
        "",
        "This lab requires browser rendering and frame-tree observation. Static HTML parsing alone is not sufficient.",
        "The evidence preserves top-page DOM, child-frame DOM snapshots, frame URLs, sandbox findings, srcdoc findings, and cross-frame rendered text.",
        "",
        "## Observed frame tree",
        "",
        "| Frame | Parent | Depth | URL | Children |",
        "|---|---|---:|---|---|",
    ]
    for frame in sorted(capture.frames, key=lambda item: (item.depth, item.frame_key)):
        parent = frame.parent_frame_key or ""
        children = ", ".join(frame.child_frame_keys)
        lines.append(f"| `{frame.frame_key}` | `{parent}` | {frame.depth} | `{frame.url}` | `{children}` |")

    lines.extend(
        [
            "",
            "## Sandbox findings",
            "",
        ]
    )
    if capture.sandbox_findings:
        for finding in capture.sandbox_findings:
            lines.append(
                f"- `{finding.iframe_selector}` sandbox=`{finding.sandbox}` src=`{finding.src}` role=`{finding.data_role or ''}`"
            )
    else:
        lines.append("- No iframe sandbox attributes observed.")

    lines.extend(
        [
            "",
            "## Srcdoc findings",
            "",
        ]
    )
    if capture.srcdoc_findings:
        for finding in capture.srcdoc_findings:
            lines.append(
                f"- `{finding.iframe_selector}` hidden_marker_present=`{finding.hidden_marker_present}` role=`{finding.data_role or ''}`"
            )
    else:
        lines.append("- No iframe srcdoc attributes observed.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This lab demonstrates why browser-AI security evaluation must preserve frame-tree evidence, not only the top page DOM.",
            "A secure browser-AI system should understand iframe boundaries, sandbox attributes, srcdoc content, and nested browsing contexts before constructing model-bound context.",
            "",
            "## What this report does not claim",
            "",
            "This helper does not perform credential collection, third-party testing, browser exploitation, or production site testing.",
            "It captures local synthetic evidence for analyst review.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_binary_artifact(writer: EvidenceWriter, relative_path: str, content: bytes) -> tuple[Path, str]:
    artifact_path = writer.out_dir / relative_path
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_bytes(content)
    return artifact_path, sha256_file(artifact_path)


def write_iframe_frame_tree_evidence(
    *,
    base_url: str,
    out_dir: str | Path,
    variant: str = "baseline",
    timeout_seconds: float = 10.0,
    renderer: FrameTreeRenderer | None = None,
) -> Path:
    """Capture an iframe/frame-tree lab run and write evidence artifacts."""

    normalized_variant = normalize_variant(variant)
    url = iframe_frame_tree_target_url(base_url, normalized_variant)
    capture = capture_iframe_frame_tree(
        url,
        variant=normalized_variant,
        timeout_seconds=timeout_seconds,
        renderer=renderer,
    )

    writer = EvidenceWriter(out_dir)
    prefix = f"iframe-frame-tree/{normalized_variant}"

    frame_tree_path, frame_tree_hash = writer.write_text_artifact(
        f"{prefix}/frame-tree.json",
        json.dumps(capture.to_dict(), indent=2, sort_keys=True) + "\n",
    )
    frame_url_list = "\n".join(frame.url for frame in capture.frames) + "\n"
    frame_url_list_path, frame_url_list_hash = writer.write_text_artifact(
        f"{prefix}/frame-url-list.txt",
        frame_url_list,
    )

    top_frame = next(frame for frame in capture.frames if frame.frame_key == "top")
    top_dom_path, top_dom_hash = writer.write_text_artifact(
        f"{prefix}/top-page-dom-snapshot.html",
        top_frame.dom_snapshot_html,
    )

    frame_snapshot_index: list[dict[str, str]] = []
    frame_snapshot_artifacts: dict[str, str] = {}
    for index, frame in enumerate((item for item in capture.frames if item.frame_key != "top"), start=1):
        snapshot_name = _safe_snapshot_name(frame, index)
        snapshot_path, snapshot_hash = writer.write_text_artifact(
            f"{prefix}/frame-dom-snapshots/{snapshot_name}",
            frame.dom_snapshot_html,
        )
        frame_snapshot_index.append(
            {
                "frame_key": frame.frame_key,
                "path": str(snapshot_path),
                "sha256": snapshot_hash,
                "url": frame.url,
            }
        )
        key = f"frame_dom_snapshot_{index:02d}"
        frame_snapshot_artifacts[key] = str(snapshot_path)
        frame_snapshot_artifacts[f"{key}_sha256"] = snapshot_hash

    frame_snapshot_index_path, frame_snapshot_index_hash = writer.write_text_artifact(
        f"{prefix}/frame-dom-snapshots/index.json",
        json.dumps(frame_snapshot_index, indent=2, sort_keys=True) + "\n",
    )
    sandbox_path, sandbox_hash = writer.write_text_artifact(
        f"{prefix}/sandbox-findings.json",
        json.dumps([asdict(item) for item in capture.sandbox_findings], indent=2, sort_keys=True) + "\n",
    )
    srcdoc_path, srcdoc_hash = writer.write_text_artifact(
        f"{prefix}/srcdoc-findings.json",
        json.dumps([asdict(item) for item in capture.srcdoc_findings], indent=2, sort_keys=True) + "\n",
    )
    cross_frame_text_path, cross_frame_text_hash = writer.write_text_artifact(
        f"{prefix}/cross-frame-rendered-text.txt",
        capture.cross_frame_rendered_text,
    )
    context_path, context_hash = writer.write_text_artifact(
        f"{prefix}/model-bound-context.txt",
        _model_bound_context(capture),
    )
    model_response_path, model_response_hash = writer.write_text_artifact(
        f"{prefix}/model-response.json",
        json.dumps(_model_response_placeholder(capture), indent=2, sort_keys=True) + "\n",
    )
    report_path, report_hash = writer.write_text_artifact(
        f"{prefix}/report.md",
        _lab_report(capture),
    )

    writer.write(
        EvidenceRecord(
            tool="ai-browser-security-suite.iframe_frame_tree",
            test_id=f"{IFRAME_FRAME_TREE_LAB_ID}.{normalized_variant}",
            supported_parts=IFRAME_FRAME_TREE_SUPPORTED_PARTS,
            target=url,
            status="observed",
            severity="info",
            summary=(
                f"Captured local iframe/frame-tree evidence for variant {normalized_variant} "
                f"with {len(capture.frames)} observed browser frames."
            ),
            evidence={
                "lab_id": capture.lab_id,
                "target_scenario_id": capture.target_scenario_id,
                "variant": capture.variant,
                "final_url": capture.final_url,
                "status_code": capture.status_code,
                "frame_count": len(capture.frames),
                "sandbox_finding_count": len(capture.sandbox_findings),
                "srcdoc_finding_count": len(capture.srcdoc_findings),
            },
            artifacts={
                "frame_tree": str(frame_tree_path),
                "frame_tree_sha256": frame_tree_hash,
                "frame_url_list": str(frame_url_list_path),
                "frame_url_list_sha256": frame_url_list_hash,
                "top_page_dom_snapshot": str(top_dom_path),
                "top_page_dom_snapshot_sha256": top_dom_hash,
                "frame_dom_snapshots_index": str(frame_snapshot_index_path),
                "frame_dom_snapshots_index_sha256": frame_snapshot_index_hash,
                **frame_snapshot_artifacts,
                "sandbox_findings": str(sandbox_path),
                "sandbox_findings_sha256": sandbox_hash,
                "srcdoc_findings": str(srcdoc_path),
                "srcdoc_findings_sha256": srcdoc_hash,
                "cross_frame_rendered_text": str(cross_frame_text_path),
                "cross_frame_rendered_text_sha256": cross_frame_text_hash,
                "model_bound_context": str(context_path),
                "model_bound_context_sha256": context_hash,
                "model_response": str(model_response_path),
                "model_response_sha256": model_response_hash,
                "report": str(report_path),
                "report_sha256": report_hash,
            },
            recommended_action=(
                "Review frame-tree JSON, frame URLs, top-page DOM, child-frame DOM snapshots, sandbox findings, "
                "srcdoc findings, and cross-frame rendered text together. A secure browser-AI control should not rely "
                "on static top-page HTML extraction alone."
            ),
        )
    )

    return writer.out_dir
