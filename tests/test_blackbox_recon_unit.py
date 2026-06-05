from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import httpx

from ai_browser_security_suite.config import Scope, Target
from ai_browser_security_suite.recon import blackbox


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int,
        url: str,
        headers: dict[str, str] | None = None,
        history: list[object] | None = None,
    ) -> None:
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}
        self.history = history or []


class FallbackClient:
    def __enter__(self) -> "FallbackClient":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def head(self, url: str) -> FakeResponse:
        return FakeResponse(status_code=405, url=url, headers={})

    def get(self, url: str) -> FakeResponse:
        return FakeResponse(
            status_code=200,
            url=f"{url.rstrip('/')}/final",
            headers={
                "content-security-policy": "default-src 'self'",
                "x-content-type-options": "nosniff",
                "server": "local-test",
                "x-ignored-header": "not-collected",
            },
            history=[SimpleNamespace(url=f"{url.rstrip('/')}/start")],
        )


class ErrorClient:
    def __enter__(self) -> "ErrorClient":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def head(self, _url: str) -> FakeResponse:
        raise httpx.ConnectError("local target unavailable")


def make_scope() -> Scope:
    return Scope(
        client_name="local-test",
        engagement_name="blackbox-recon-unit",
        authorization_reference="local-owned-target",
        passive_only_default=True,
        targets=[
            Target(
                name="loopback",
                fqdn="127.0.0.1",
                allowed_ips=["127.0.0.1"],
                allowed_paths=["/health"],
                scheme="http",
                ports=[11435],
            )
        ],
    )


def test_probe_http_falls_back_to_get_when_head_is_not_useful(monkeypatch) -> None:
    monkeypatch.setattr(blackbox.httpx, "Client", lambda **_kwargs: FallbackClient())

    result = blackbox.probe_http("http://127.0.0.1:11435/health", passive_only=True)

    assert result["url"] == "http://127.0.0.1:11435/health"
    assert result["final_url"] == "http://127.0.0.1:11435/health/final"
    assert result["status_code"] == 200
    assert result["redirect_chain"] == ["http://127.0.0.1:11435/health/start"]
    assert result["passive_only"] is True
    assert result["headers"] == {
        "content-security-policy": "default-src 'self'",
        "x-content-type-options": "nosniff",
        "server": "local-test",
    }


def test_probe_http_returns_error_structure_for_local_connection_failure(monkeypatch) -> None:
    monkeypatch.setattr(blackbox.httpx, "Client", lambda **_kwargs: ErrorClient())

    result = blackbox.probe_http("http://127.0.0.1:11435/health", passive_only=True)

    assert "error" in result
    assert "local target unavailable" in result["error"]


def test_run_blackbox_recon_writes_dns_and_http_evidence_without_network(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(blackbox, "resolve_fqdn", lambda _fqdn: ["127.0.0.1", "10.0.0.5"])
    monkeypatch.setattr(
        blackbox,
        "probe_http",
        lambda url, passive_only: {
            "url": url,
            "final_url": url,
            "status_code": 200,
            "redirect_chain": [],
            "headers": {"x-content-type-options": "nosniff"},
            "passive_only": passive_only,
        },
    )

    evidence_path = blackbox.run_blackbox_recon(make_scope(), tmp_path, passive_only=True)

    assert evidence_path == tmp_path / "evidence.jsonl"
    records = [
        json.loads(line)
        for line in evidence_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert [record["test_id"] for record in records] == [
        "dns-resolution",
        "http-security-headers",
    ]
    assert records[0]["severity"] == "review"
    assert records[0]["evidence"]["unexpected_addresses"] == ["10.0.0.5"]
    assert records[1]["target"] == "http://127.0.0.1:11435/health"
    assert "content-security-policy" in records[1]["evidence"]["missing_recommended_headers"]
