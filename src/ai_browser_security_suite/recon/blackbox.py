# File: src/ai_browser_security_suite/recon/blackbox.py
# Change description: safe authorized black-box recon for client-provided targets.
# Git commit comment: add blue team black box mvp foundation
from __future__ import annotations
import socket
import ssl
from pathlib import Path
from urllib.parse import urljoin
import dns.resolver
import httpx
from ai_browser_security_suite.config import Scope
from ai_browser_security_suite.evidence import EvidenceRecord, EvidenceWriter

def resolve_fqdn(fqdn: str) -> list[str]:
    addresses = []
    resolver = dns.resolver.Resolver()
    for record_type in ("A", "AAAA"):
        try:
            addresses.extend(str(answer) for answer in resolver.resolve(fqdn, record_type))
        except Exception:
            pass
    return sorted(set(addresses))

def probe_tls(fqdn: str, port: int) -> dict[str, str]:
    context = ssl.create_default_context()
    with socket.create_connection((fqdn, port), timeout=10) as raw_socket:
        with context.wrap_socket(raw_socket, server_hostname=fqdn) as tls_socket:
            certificate = tls_socket.getpeercert()
            return {"tls_version": str(tls_socket.version()), "cipher": str(tls_socket.cipher()), "not_before": str(certificate.get("notBefore", "")), "not_after": str(certificate.get("notAfter", "")), "subject": str(certificate.get("subject", [])), "issuer": str(certificate.get("issuer", []))}

def probe_http(url: str, passive_only: bool) -> dict[str, object]:
    interesting = {"content-security-policy", "strict-transport-security", "x-frame-options", "x-content-type-options", "referrer-policy", "permissions-policy", "cross-origin-opener-policy", "cross-origin-resource-policy", "cross-origin-embedder-policy", "server"}
    with httpx.Client(follow_redirects=True, timeout=15) as client:
        try:
            response = client.head(url)
            if response.status_code in (403, 405) or not response.headers:
                response = client.get(url)
        except httpx.HTTPError as exc:
            return {"error": str(exc)}
    return {"url": url, "final_url": str(response.url), "status_code": response.status_code, "redirect_chain": [str(item.url) for item in response.history], "headers": {key: value for key, value in response.headers.items() if key.lower() in interesting}, "passive_only": passive_only}

def run_blackbox_recon(scope: Scope, out_dir: str | Path, passive_only: bool) -> Path:
    writer = EvidenceWriter(out_dir)
    for target in scope.targets:
        resolved = resolve_fqdn(target.fqdn)
        unexpected = sorted(set(resolved) - set(target.allowed_ips)) if target.allowed_ips else []
        writer.write(EvidenceRecord(tool="blackbox-recon", test_id="dns-resolution", supported_parts=["Part 06", "Part 23", "Part 24", "Part 26", "Part 27"], target=target.fqdn, status="observed", severity="info" if not unexpected else "review", summary="Resolved target FQDN and compared observed addresses with client-provided allowed IPs.", evidence={"resolved_addresses": resolved, "allowed_ips": target.allowed_ips, "unexpected_addresses": unexpected}, recommended_action="Confirm all resolved addresses are intended protected browser, proxy, tenant, or lab-hosting endpoints."))
        for port in target.ports:
            if target.scheme == "https":
                try:
                    tls_info = probe_tls(target.fqdn, port)
                    status, severity, summary = "observed", "info", "Collected TLS certificate, protocol, and cipher information."
                except Exception as exc:
                    tls_info = {"error": str(exc)}
                    status, severity, summary = "error", "review", "TLS probe failed."
                writer.write(EvidenceRecord(tool="blackbox-recon", test_id="tls-posture", supported_parts=["Part 23", "Part 24", "Part 26", "Part 27"], target=f"{target.fqdn}:{port}", status=status, severity=severity, summary=summary, evidence=tls_info, recommended_action="Review TLS version, certificate validity, issuer, and whether the path matches expected protected browser infrastructure."))
        for base_url in target.base_urls():
            for allowed_path in target.allowed_paths:
                url = urljoin(base_url + "/", allowed_path.lstrip("/"))
                http_info = probe_http(url, passive_only)
                headers = {key.lower(): value for key, value in http_info.get("headers", {}).items()}
                missing = [header for header in ["strict-transport-security", "content-security-policy", "x-content-type-options", "referrer-policy"] if header not in headers]
                writer.write(EvidenceRecord(tool="blackbox-recon", test_id="http-security-headers", supported_parts=["Part 06", "Part 12", "Part 23", "Part 24", "Part 26", "Part 27"], target=url, status="observed", severity="info" if not missing else "review", summary="Collected HTTP status, redirects, and browser-relevant security headers.", evidence={"http": http_info, "missing_recommended_headers": missing}, recommended_action="Validate whether missing headers are expected for the protected browser path and whether they affect AI browser rendering, framing, isolation, or evidence quality."))
    return Path(out_dir) / "evidence.jsonl"
