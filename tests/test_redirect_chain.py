from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import httpx
import pytest

from ai_browser_security_suite.redirect_chain import (
    REDIRECT_CHAIN_LAB_ID,
    REDIRECT_CHAIN_TARGET_SCENARIO_ID,
    RedirectChainError,
    capture_redirect_chain,
    redirect_start_url,
    write_redirect_chain_evidence,
)


def _mock_redirect_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        query = str(request.url.query.decode() if isinstance(request.url.query, bytes) else request.url.query)
        variant = "baseline"
        if "variant=encoded" in query:
            variant = "encoded"
        elif "variant=slow" in query:
            variant = "slow"

        headers = {
            "X-Browser-Safe-Lab": REDIRECT_CHAIN_LAB_ID,
            "X-Browser-Safe-Scenario": REDIRECT_CHAIN_TARGET_SCENARIO_ID,
        }
        if path == "/browser-safe/redirect/start":
            return httpx.Response(
                302,
                headers={
                    **headers,
                    "X-Browser-Safe-Hop": "start",
                    "Location": f"/browser-safe/redirect/hop/1?variant={variant}",
                },
                request=request,
            )
        if path == "/browser-safe/redirect/hop/1":
            return httpx.Response(
                302,
                headers={
                    **headers,
                    "X-Browser-Safe-Hop": "1",
                    "Location": f"/browser-safe/redirect/hop/2?variant={variant}",
                },
                request=request,
            )
        if path == "/browser-safe/redirect/hop/2":
            return httpx.Response(
                302,
                headers={
                    **headers,
                    "X-Browser-Safe-Hop": "2",
                    "Location": f"/browser-safe/redirect/final?variant={variant}",
                },
                request=request,
            )
        if path == "/browser-safe/redirect/final":
            return httpx.Response(
                200,
                headers={**headers, "X-Browser-Safe-Hop": "final"},
                text=(
                    "<html><body><h1>Browser-Safe AI Redirect Chain Lab</h1>"
                    f"<p>scenario={REDIRECT_CHAIN_TARGET_SCENARIO_ID}</p>"
                    f"<p>lab={REDIRECT_CHAIN_LAB_ID}</p>"
                    f"<p>variant={variant}</p></body></html>"
                ),
                request=request,
            )
        return httpx.Response(404, text="not found", request=request)

    return httpx.MockTransport(handler)


def test_redirect_start_url_requires_loopback() -> None:
    assert redirect_start_url("http://127.0.0.1:11435", "baseline").endswith(
        "/browser-safe/redirect/start?variant=baseline"
    )
    with pytest.raises(RedirectChainError, match="loopback URL"):
        redirect_start_url("https://example.com", "baseline")


def test_capture_redirect_chain_records_hops() -> None:
    client = httpx.Client(transport=_mock_redirect_transport(), follow_redirects=False)
    capture = capture_redirect_chain(
        "http://127.0.0.1:11435/browser-safe/redirect/start?variant=encoded",
        variant="encoded",
        client=client,
    )

    assert capture.lab_id == REDIRECT_CHAIN_LAB_ID
    assert capture.target_scenario_id == REDIRECT_CHAIN_TARGET_SCENARIO_ID
    assert capture.variant == "encoded"
    assert capture.final_status_code == 200
    assert capture.hop_count == 4
    assert [hop.status_code for hop in capture.hops] == [302, 302, 302, 200]
    assert capture.hops[-1].browser_safe_hop == "final"
    assert "variant=encoded" in capture.final_page_html


def test_capture_redirect_chain_rejects_external_redirect() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"Location": "https://example.com/evil"}, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False)

    with pytest.raises(RedirectChainError, match="Location must be a loopback URL"):
        capture_redirect_chain(
            "http://127.0.0.1:11435/browser-safe/redirect/start?variant=baseline",
            client=client,
        )


def test_write_redirect_chain_evidence_outputs_manifest(tmp_path: Path) -> None:
    client = httpx.Client(transport=_mock_redirect_transport(), follow_redirects=False)
    out_dir = write_redirect_chain_evidence(
        base_url="http://127.0.0.1:11435",
        out_dir=tmp_path,
        variant="slow",
        client=client,
    )

    evidence_jsonl = out_dir / "evidence.jsonl"
    manifest_json = out_dir / "artifact-manifest.json"
    assert evidence_jsonl.exists()
    assert manifest_json.exists()

    record = json.loads(evidence_jsonl.read_text(encoding="utf-8").strip())
    assert record["test_id"] == "guided.redirect_chain_evidence.slow"
    assert record["evidence"]["target_scenario_id"] == "browser.redirect_chain"
    assert record["evidence"]["variant"] == "slow"
    assert record["evidence"]["hop_count"] == 4

    manifest = json.loads(manifest_json.read_text(encoding="utf-8"))
    artifact_paths = {artifact["path"] for artifact in manifest["artifacts"]}
    assert "redirect-chain/slow/redirect-chain.json" in artifact_paths
    assert "redirect-chain/slow/http-status-sequence.txt" in artifact_paths
    assert "redirect-chain/slow/final-url.txt" in artifact_paths
    assert "redirect-chain/slow/final-page.html" in artifact_paths
    assert "redirect-chain/slow/model-bound-context.txt" in artifact_paths
    assert "redirect-chain/slow/model-response.json" in artifact_paths
    assert "redirect-chain/slow/report.md" in artifact_paths

    chain = json.loads((out_dir / "redirect-chain/slow/redirect-chain.json").read_text(encoding="utf-8"))
    assert chain["target_scenario_id"] == "browser.redirect_chain"
    assert chain["variant"] == "slow"
    assert chain["hop_count"] == 4
