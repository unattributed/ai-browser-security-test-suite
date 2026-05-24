from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_browser_security_suite.storage_state_boundary import (
    STORAGE_STATE_BOUNDARY_COOKIE_NAME,
    STORAGE_STATE_BOUNDARY_LAB_ID,
    STORAGE_STATE_BOUNDARY_LOCAL_KEY,
    STORAGE_STATE_BOUNDARY_PROTECTED_VALUES,
    STORAGE_STATE_BOUNDARY_SESSION_KEY,
    STORAGE_STATE_BOUNDARY_TARGET_SCENARIO_ID,
    BrowserStateSnapshot,
    BrowserStorageStateEvidence,
    StorageStateBoundaryError,
    capture_storage_state_boundary,
    storage_state_boundary_target_url,
    write_storage_state_boundary_evidence,
)


def _after_state_for_variant(variant: str) -> BrowserStateSnapshot:
    cookies = ()
    local_storage: dict[str, str] = {}
    session_storage: dict[str, str] = {}
    cache_like: dict[str, object] = {
        "supported": True,
        "cache_name": "bsai-storage-state-boundary-cache",
        "request_path": "/browser-safe/storage-state-boundary/cache-marker.txt",
        "present": False,
        "value": "",
    }

    if variant in {"cookie_state_boundary", "combined_state_boundary"}:
        cookies = (
            {
                "name": STORAGE_STATE_BOUNDARY_COOKIE_NAME,
                "value": STORAGE_STATE_BOUNDARY_PROTECTED_VALUES["cookie"],
                "domain": "127.0.0.1",
                "path": "/browser-safe/storage-state-boundary",
            },
        )
    if variant in {"local_storage_state_boundary", "combined_state_boundary"}:
        local_storage[STORAGE_STATE_BOUNDARY_LOCAL_KEY] = STORAGE_STATE_BOUNDARY_PROTECTED_VALUES["local_storage"]
    if variant in {"session_storage_state_boundary", "combined_state_boundary"}:
        session_storage[STORAGE_STATE_BOUNDARY_SESSION_KEY] = STORAGE_STATE_BOUNDARY_PROTECTED_VALUES["session_storage"]
    if variant == "combined_state_boundary":
        cache_like = {
            "supported": True,
            "cache_name": "bsai-storage-state-boundary-cache",
            "request_path": "/browser-safe/storage-state-boundary/cache-marker.txt",
            "present": True,
            "value": STORAGE_STATE_BOUNDARY_PROTECTED_VALUES["cache_like"],
        }

    return BrowserStateSnapshot(
        cookies=cookies,
        local_storage=local_storage,
        session_storage=session_storage,
        cache_like=cache_like,
    )


class FakeStorageStateRenderer:
    def __init__(
        self,
        *,
        variant: str = "combined_state_boundary",
        headers: dict[str, str] | None = None,
        final_url: str | None = None,
        status_code: int = 200,
        model_bound_context: str | None = None,
        state_after: BrowserStateSnapshot | None = None,
        state_write_status: str = "complete",
        blocked_external_urls: tuple[str, ...] = (),
    ) -> None:
        self.variant = variant
        self.headers = headers or {
            "X-Browser-Safe-Lab": STORAGE_STATE_BOUNDARY_LAB_ID,
            "X-Browser-Safe-Scenario": STORAGE_STATE_BOUNDARY_TARGET_SCENARIO_ID,
            "X-Browser-Safe-Variant": variant,
        }
        self.final_url = final_url or (
            f"http://127.0.0.1:11435/browser-safe/storage-state-boundary?variant={variant}"
        )
        self.status_code = status_code
        self.model_bound_context = model_bound_context or (
            "Model-bound context preview\n"
            f"Scenario id: {STORAGE_STATE_BOUNDARY_TARGET_SCENARIO_ID}\n"
            f"Guided lab id: {STORAGE_STATE_BOUNDARY_LAB_ID}\n"
            f"Variant: {variant}\n"
            "Cookie observation required: true\n"
        )
        self.state_after = state_after or _after_state_for_variant(variant)
        self.state_write_status = state_write_status
        self.blocked_external_urls = blocked_external_urls

    def capture_storage_state(
        self,
        url: str,
        *,
        timeout_seconds: float = 10.0,
    ) -> BrowserStorageStateEvidence:
        return BrowserStorageStateEvidence(
            url=url,
            final_url=self.final_url,
            status_code=self.status_code,
            response_headers=self.headers,
            browser_state_before=BrowserStateSnapshot(
                cookies=(),
                local_storage={},
                session_storage={},
                cache_like={
                    "supported": True,
                    "cache_name": "bsai-storage-state-boundary-cache",
                    "request_path": "/browser-safe/storage-state-boundary/cache-marker.txt",
                    "present": False,
                    "value": "",
                },
            ),
            browser_state_after=self.state_after,
            dom_snapshot_html="<html><body><section id='model-bound-context'>metadata only</section></body></html>",
            rendered_text="Browser-Safe AI Storage State Boundary Lab",
            model_bound_context=self.model_bound_context,
            state_write_status=self.state_write_status,
            state_write_status_text="Synthetic browser state was seeded for evidence capture.",
            screenshot_png=b"\x89PNG\r\n\x1a\nfake-storage-state-screenshot",
            blocked_external_urls=self.blocked_external_urls,
        )


def test_storage_state_boundary_target_url_requires_loopback() -> None:
    assert storage_state_boundary_target_url(
        "http://127.0.0.1:11435",
        "combined_state_boundary",
    ).endswith("/browser-safe/storage-state-boundary?variant=combined_state_boundary")
    with pytest.raises(StorageStateBoundaryError, match="loopback URL"):
        storage_state_boundary_target_url("https://example.com", "combined_state_boundary")


def test_capture_storage_state_boundary_records_combined_state() -> None:
    capture = capture_storage_state_boundary(
        "http://127.0.0.1:11435/browser-safe/storage-state-boundary?variant=combined_state_boundary",
        variant="combined_state_boundary",
        renderer=FakeStorageStateRenderer(),
    )

    assert capture.lab_id == STORAGE_STATE_BOUNDARY_LAB_ID
    assert capture.target_scenario_id == STORAGE_STATE_BOUNDARY_TARGET_SCENARIO_ID
    assert capture.variant == "combined_state_boundary"
    assert capture.cookie_findings["observed_protected_value"] is True
    assert capture.local_storage_findings["observed_protected_value"] is True
    assert capture.session_storage_findings["observed_protected_value"] is True
    assert capture.cache_like_findings["observed_protected_value"] is True
    assert capture.state_boundary_findings["status"] == "boundary-preserved"
    assert capture.state_boundary_findings["model_bound_context_leak_count"] == 0


def test_capture_storage_state_boundary_records_baseline_no_state() -> None:
    capture = capture_storage_state_boundary(
        "http://127.0.0.1:11435/browser-safe/storage-state-boundary?variant=baseline_no_state",
        variant="baseline_no_state",
        renderer=FakeStorageStateRenderer(variant="baseline_no_state"),
    )

    assert capture.storage_state_summary["after_observed_state"] == {
        "cookie": False,
        "local_storage": False,
        "session_storage": False,
        "cache_like": False,
    }
    assert capture.state_boundary_findings["status"] == "boundary-preserved"


def test_capture_storage_state_boundary_rejects_wrong_target_headers() -> None:
    renderer = FakeStorageStateRenderer(
        headers={
            "X-Browser-Safe-Lab": STORAGE_STATE_BOUNDARY_LAB_ID,
            "X-Browser-Safe-Scenario": "browser.dom_render_mismatch",
            "X-Browser-Safe-Variant": "combined_state_boundary",
        }
    )
    with pytest.raises(StorageStateBoundaryError, match="X-Browser-Safe-Scenario"):
        capture_storage_state_boundary(
            "http://127.0.0.1:11435/browser-safe/storage-state-boundary?variant=combined_state_boundary",
            variant="combined_state_boundary",
            renderer=renderer,
        )


def test_capture_storage_state_boundary_rejects_external_final_url() -> None:
    renderer = FakeStorageStateRenderer(final_url="https://example.com/storage")
    with pytest.raises(StorageStateBoundaryError, match="final URL must be a loopback URL"):
        capture_storage_state_boundary(
            "http://127.0.0.1:11435/browser-safe/storage-state-boundary?variant=combined_state_boundary",
            variant="combined_state_boundary",
            renderer=renderer,
        )


def test_capture_storage_state_boundary_rejects_blocked_external_request() -> None:
    renderer = FakeStorageStateRenderer(blocked_external_urls=("https://example.com/tracker.js",))
    with pytest.raises(StorageStateBoundaryError, match="external URL load"):
        capture_storage_state_boundary(
            "http://127.0.0.1:11435/browser-safe/storage-state-boundary?variant=combined_state_boundary",
            variant="combined_state_boundary",
            renderer=renderer,
        )


def test_capture_storage_state_boundary_rejects_model_context_leak() -> None:
    renderer = FakeStorageStateRenderer(
        model_bound_context=(
            "metadata only "
            + STORAGE_STATE_BOUNDARY_PROTECTED_VALUES["local_storage"]
        )
    )
    with pytest.raises(StorageStateBoundaryError, match="protected-state-leak"):
        capture_storage_state_boundary(
            "http://127.0.0.1:11435/browser-safe/storage-state-boundary?variant=combined_state_boundary",
            variant="combined_state_boundary",
            renderer=renderer,
        )


def test_capture_storage_state_boundary_rejects_missing_expected_state() -> None:
    renderer = FakeStorageStateRenderer(
        state_after=BrowserStateSnapshot(
            cookies=(),
            local_storage={},
            session_storage={},
            cache_like={
                "supported": True,
                "cache_name": "bsai-storage-state-boundary-cache",
                "request_path": "/browser-safe/storage-state-boundary/cache-marker.txt",
                "present": False,
                "value": "",
            },
        )
    )
    with pytest.raises(StorageStateBoundaryError, match="evidence-incomplete"):
        capture_storage_state_boundary(
            "http://127.0.0.1:11435/browser-safe/storage-state-boundary?variant=combined_state_boundary",
            variant="combined_state_boundary",
            renderer=renderer,
        )


def test_write_storage_state_boundary_evidence_outputs_manifest(tmp_path: Path) -> None:
    out_dir = write_storage_state_boundary_evidence(
        base_url="http://127.0.0.1:11435",
        out_dir=tmp_path,
        variant="combined_state_boundary",
        renderer=FakeStorageStateRenderer(),
    )

    evidence_jsonl = out_dir / "evidence.jsonl"
    manifest_json = out_dir / "artifact-manifest.json"
    context_path = out_dir / "storage-state-boundary/combined_state_boundary/model-bound-context.txt"
    assert evidence_jsonl.exists()
    assert manifest_json.exists()
    assert context_path.exists()

    context = context_path.read_text(encoding="utf-8")
    for protected_value in STORAGE_STATE_BOUNDARY_PROTECTED_VALUES.values():
        assert protected_value not in context

    record = json.loads(evidence_jsonl.read_text(encoding="utf-8").strip())
    assert record["test_id"] == "guided.storage_state_boundary_evidence.combined_state_boundary"
    assert record["evidence"]["target_scenario_id"] == "browser.storage_state_boundary"
    assert record["evidence"]["variant"] == "combined_state_boundary"
    assert record["evidence"]["boundary_status"] == "boundary-preserved"
    assert record["evidence"]["model_bound_context_leak_count"] == 0

    manifest = json.loads(manifest_json.read_text(encoding="utf-8"))
    artifact_paths = {artifact["path"] for artifact in manifest["artifacts"]}
    assert "storage-state-boundary/combined_state_boundary/storage-state-summary.json" in artifact_paths
    assert "storage-state-boundary/combined_state_boundary/cookie-findings.json" in artifact_paths
    assert "storage-state-boundary/combined_state_boundary/local-storage-findings.json" in artifact_paths
    assert "storage-state-boundary/combined_state_boundary/session-storage-findings.json" in artifact_paths
    assert "storage-state-boundary/combined_state_boundary/browser-state-before.json" in artifact_paths
    assert "storage-state-boundary/combined_state_boundary/browser-state-after.json" in artifact_paths
    assert "storage-state-boundary/combined_state_boundary/model-bound-context.txt" in artifact_paths
    assert "storage-state-boundary/combined_state_boundary/model-response.json" in artifact_paths
    assert "storage-state-boundary/combined_state_boundary/state-boundary-findings.json" in artifact_paths
    assert "storage-state-boundary/combined_state_boundary/report.md" in artifact_paths
