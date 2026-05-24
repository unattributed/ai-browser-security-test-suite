from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_browser_security_suite.iframe_frame_tree import (
    BrowserFrameTreeEvidence,
    FrameNodeEvidence,
    IFRAME_FRAME_TREE_LAB_ID,
    IFRAME_FRAME_TREE_TARGET_SCENARIO_ID,
    IframeFrameTreeError,
    SandboxFinding,
    SrcdocFinding,
    capture_iframe_frame_tree,
    iframe_frame_tree_target_url,
    write_iframe_frame_tree_evidence,
)


class FakeFrameTreeRenderer:
    def __init__(
        self,
        *,
        headers: dict[str, str] | None = None,
        final_url: str = "http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=srcdoc_hidden_context",
        status_code: int = 200,
        frames: tuple[FrameNodeEvidence, ...] | None = None,
        sandbox_findings: tuple[SandboxFinding, ...] = (),
        srcdoc_findings: tuple[SrcdocFinding, ...] = (),
        blocked_external_urls: tuple[str, ...] = (),
    ) -> None:
        self.headers = headers or {
            "X-Browser-Safe-Lab": IFRAME_FRAME_TREE_LAB_ID,
            "X-Browser-Safe-Scenario": IFRAME_FRAME_TREE_TARGET_SCENARIO_ID,
            "X-Browser-Safe-Variant": "srcdoc_hidden_context",
        }
        self.final_url = final_url
        self.status_code = status_code
        self.frames = frames or (
            FrameNodeEvidence(
                frame_key="top",
                parent_frame_key=None,
                depth=0,
                name="",
                url="http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=srcdoc_hidden_context",
                title_text="Browser-Safe AI Iframe Frame-Tree Lab",
                dom_snapshot_html="<html><body><iframe id='frame-srcdoc-child' srcdoc='child'></iframe></body></html>",
                rendered_text="Top visible text",
                child_frame_keys=("frame-1",),
            ),
            FrameNodeEvidence(
                frame_key="frame-1",
                parent_frame_key="top",
                depth=1,
                name="frame-srcdoc-child",
                url="about:srcdoc",
                title_text="Browser-Safe srcdoc frame",
                dom_snapshot_html="<html><body><p>srcdoc visible text</p><p hidden>hidden marker</p></body></html>",
                rendered_text="srcdoc visible text",
                child_frame_keys=(),
            ),
        )
        self.sandbox_findings = sandbox_findings
        self.srcdoc_findings = srcdoc_findings or (
            SrcdocFinding(
                parent_frame_key="top",
                iframe_selector="#frame-srcdoc-child",
                iframe_id="frame-srcdoc-child",
                iframe_name="frame-srcdoc-child",
                iframe_title="Browser-Safe srcdoc hidden context frame",
                srcdoc_excerpt="Synthetic hidden srcdoc marker",
                hidden_marker_present=True,
                data_role="srcdoc-child",
            ),
        )
        self.blocked_external_urls = blocked_external_urls

    def capture_frame_tree(self, url: str, *, timeout_seconds: float = 10.0) -> BrowserFrameTreeEvidence:
        return BrowserFrameTreeEvidence(
            url=url,
            final_url=self.final_url,
            status_code=self.status_code,
            response_headers=self.headers,
            frames=self.frames,
            sandbox_findings=self.sandbox_findings,
            srcdoc_findings=self.srcdoc_findings,
            blocked_external_urls=self.blocked_external_urls,
        )


def test_iframe_frame_tree_target_url_requires_loopback() -> None:
    assert iframe_frame_tree_target_url("http://127.0.0.1:11435", "baseline").endswith(
        "/browser-safe/iframe-frame-tree?variant=baseline"
    )
    with pytest.raises(IframeFrameTreeError, match="loopback URL"):
        iframe_frame_tree_target_url("https://example.com", "baseline")


def test_capture_iframe_frame_tree_records_frames() -> None:
    renderer = FakeFrameTreeRenderer()
    capture = capture_iframe_frame_tree(
        "http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=srcdoc_hidden_context",
        variant="srcdoc_hidden_context",
        renderer=renderer,
    )

    assert capture.lab_id == IFRAME_FRAME_TREE_LAB_ID
    assert capture.target_scenario_id == IFRAME_FRAME_TREE_TARGET_SCENARIO_ID
    assert capture.variant == "srcdoc_hidden_context"
    assert len(capture.frames) == 2
    assert capture.frames[0].frame_key == "top"
    assert capture.frames[1].url == "about:srcdoc"
    assert len(capture.srcdoc_findings) == 1
    assert "frame-1" in capture.cross_frame_rendered_text


def test_capture_iframe_frame_tree_rejects_wrong_target_headers() -> None:
    renderer = FakeFrameTreeRenderer(headers={
        "X-Browser-Safe-Lab": IFRAME_FRAME_TREE_LAB_ID,
        "X-Browser-Safe-Scenario": "browser.dom_render_mismatch",
        "X-Browser-Safe-Variant": "srcdoc_hidden_context",
    })
    with pytest.raises(IframeFrameTreeError, match="X-Browser-Safe-Scenario"):
        capture_iframe_frame_tree(
            "http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=srcdoc_hidden_context",
            variant="srcdoc_hidden_context",
            renderer=renderer,
        )


def test_capture_iframe_frame_tree_rejects_external_frame_url() -> None:
    frames = (
        FrameNodeEvidence(
            frame_key="top",
            parent_frame_key=None,
            depth=0,
            name="",
            url="http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=baseline",
            title_text="top",
            dom_snapshot_html="<html></html>",
            rendered_text="top",
            child_frame_keys=("frame-1",),
        ),
        FrameNodeEvidence(
            frame_key="frame-1",
            parent_frame_key="top",
            depth=1,
            name="external",
            url="https://example.com/frame",
            title_text="external",
            dom_snapshot_html="<html></html>",
            rendered_text="external",
            child_frame_keys=(),
        ),
    )
    renderer = FakeFrameTreeRenderer(
        headers={
            "X-Browser-Safe-Lab": IFRAME_FRAME_TREE_LAB_ID,
            "X-Browser-Safe-Scenario": IFRAME_FRAME_TREE_TARGET_SCENARIO_ID,
            "X-Browser-Safe-Variant": "baseline",
        },
        final_url="http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=baseline",
        frames=frames,
        srcdoc_findings=(),
    )
    with pytest.raises(IframeFrameTreeError, match="frame frame-1 URL"):
        capture_iframe_frame_tree(
            "http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=baseline",
            variant="baseline",
            renderer=renderer,
        )


def test_capture_iframe_frame_tree_rejects_blocked_external_request() -> None:
    renderer = FakeFrameTreeRenderer(blocked_external_urls=("https://example.com/tracker.js",))
    with pytest.raises(IframeFrameTreeError, match="external URL load"):
        capture_iframe_frame_tree(
            "http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=srcdoc_hidden_context",
            variant="srcdoc_hidden_context",
            renderer=renderer,
        )


def test_capture_iframe_frame_tree_rejects_http_error_status() -> None:
    renderer = FakeFrameTreeRenderer(status_code=500)
    with pytest.raises(IframeFrameTreeError, match="HTTP 500"):
        capture_iframe_frame_tree(
            "http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=srcdoc_hidden_context",
            variant="srcdoc_hidden_context",
            renderer=renderer,
        )


def test_write_iframe_frame_tree_evidence_outputs_manifest(tmp_path: Path) -> None:
    out_dir = write_iframe_frame_tree_evidence(
        base_url="http://127.0.0.1:11435",
        out_dir=tmp_path,
        variant="srcdoc_hidden_context",
        renderer=FakeFrameTreeRenderer(),
    )

    evidence_jsonl = out_dir / "evidence.jsonl"
    manifest_json = out_dir / "artifact-manifest.json"
    assert evidence_jsonl.exists()
    assert manifest_json.exists()

    record = json.loads(evidence_jsonl.read_text(encoding="utf-8").strip())
    assert record["test_id"] == "guided.iframe_frame_tree_evidence.srcdoc_hidden_context"
    assert record["evidence"]["target_scenario_id"] == "browser.iframe_frame_tree"
    assert record["evidence"]["variant"] == "srcdoc_hidden_context"
    assert record["evidence"]["frame_count"] == 2
    assert record["evidence"]["srcdoc_finding_count"] == 1

    manifest = json.loads(manifest_json.read_text(encoding="utf-8"))
    artifact_paths = {artifact["path"] for artifact in manifest["artifacts"]}
    assert "iframe-frame-tree/srcdoc_hidden_context/frame-tree.json" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/frame-url-list.txt" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/top-page-dom-snapshot.html" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/frame-dom-snapshots/index.json" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/frame-dom-snapshots/01-frame-1.html" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/sandbox-findings.json" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/srcdoc-findings.json" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/cross-frame-rendered-text.txt" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/model-bound-context.txt" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/model-response.json" in artifact_paths
    assert "iframe-frame-tree/srcdoc_hidden_context/report.md" in artifact_paths

    report = (out_dir / "iframe-frame-tree/srcdoc_hidden_context/report.md").read_text(encoding="utf-8")
    assert "frame-tree observation" in report
    assert "Static HTML parsing alone is not sufficient" in report
