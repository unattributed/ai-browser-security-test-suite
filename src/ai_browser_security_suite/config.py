# File: src/ai_browser_security_suite/config.py
# Change description: define scope models for authorized browser-AI validation.
# Git commit comment: add blue team black box mvp foundation
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import ipaddress
import os
import yaml

class ScopeError(ValueError):
    pass

@dataclass(frozen=True)
class CredentialRef:
    name: str
    username_env: str | None = None
    password_env: str | None = None
    token_env: str | None = None
    notes: str | None = None

    def resolve(self) -> dict[str, str]:
        resolved = {}
        for key, env_name in (("username", self.username_env), ("password", self.password_env), ("token", self.token_env)):
            if env_name and os.getenv(env_name):
                resolved[key] = os.environ[env_name]
        return resolved

@dataclass(frozen=True)
class Target:
    name: str
    fqdn: str
    allowed_ips: list[str] = field(default_factory=list)
    allowed_paths: list[str] = field(default_factory=lambda: ["/"])
    scheme: str = "https"
    ports: list[int] = field(default_factory=lambda: [443])
    credential_ref: str | None = None
    tags: list[str] = field(default_factory=list)

    def base_urls(self) -> list[str]:
        urls = []
        for port in self.ports:
            if (self.scheme == "https" and port == 443) or (self.scheme == "http" and port == 80):
                urls.append(f"{self.scheme}://{self.fqdn}")
            else:
                urls.append(f"{self.scheme}://{self.fqdn}:{port}")
        return urls

    def validate_allowed_ips(self) -> None:
        for raw_ip in self.allowed_ips:
            try:
                ipaddress.ip_address(raw_ip)
            except ValueError as exc:
                raise ScopeError(f"invalid IP for {self.name}: {raw_ip}") from exc

@dataclass(frozen=True)
class Scope:
    client_name: str
    engagement_name: str
    authorization_reference: str
    passive_only_default: bool
    targets: list[Target]
    credential_refs: list[CredentialRef] = field(default_factory=list)
    prohibited_actions: list[str] = field(default_factory=list)
    notes: str | None = None

    def require_authorization(self, active_requested: bool, authorization_flag: bool) -> None:
        if not active_requested:
            return
        if self.passive_only_default and not authorization_flag:
            raise ScopeError("active testing refused: --i-have-authorization is required")
        if not self.authorization_reference.strip():
            raise ScopeError("active testing refused: authorization_reference is empty")

def load_scope(path: str | Path) -> Scope:
    scope_path = Path(path)
    if not scope_path.exists():
        raise ScopeError(f"scope file not found: {scope_path}")
    raw = yaml.safe_load(scope_path.read_text(encoding="utf-8")) or {}
    targets = []
    for item in raw.get("targets", []):
        target = Target(
            name=str(item["name"]),
            fqdn=str(item["fqdn"]),
            allowed_ips=[str(value) for value in item.get("allowed_ips", [])],
            allowed_paths=[str(value) for value in item.get("allowed_paths", ["/"])],
            scheme=str(item.get("scheme", "https")),
            ports=[int(value) for value in item.get("ports", [443])],
            credential_ref=item.get("credential_ref"),
            tags=[str(value) for value in item.get("tags", [])],
        )
        target.validate_allowed_ips()
        targets.append(target)
    if not targets:
        raise ScopeError("scope file must contain at least one target")
    credentials = [CredentialRef(name=str(item["name"]), username_env=item.get("username_env"), password_env=item.get("password_env"), token_env=item.get("token_env"), notes=item.get("notes")) for item in raw.get("credential_refs", [])]
    return Scope(
        client_name=str(raw.get("client_name", "unknown-client")),
        engagement_name=str(raw.get("engagement_name", "browser-ai-validation")),
        authorization_reference=str(raw.get("authorization_reference", "")),
        passive_only_default=bool(raw.get("passive_only_default", True)),
        targets=targets,
        credential_refs=credentials,
        prohibited_actions=[str(value) for value in raw.get("prohibited_actions", [])],
        notes=raw.get("notes"),
    )

def write_scope_template(path: str | Path) -> None:
    scope_path = Path(path)
    scope_path.parent.mkdir(parents=True, exist_ok=True)
    scope_path.write_text("""---
client_name: example organization
engagement_name: browser ai ecosystem validation
authorization_reference: roe-ticket-or-sow-reference
passive_only_default: true
notes: replace with client-provided FQDNs, IPs, paths, ports, and test credential env vars.
credential_refs:
  - name: test-user-1
    username_env: BAI_TEST_USERNAME
    password_env: BAI_TEST_PASSWORD
    token_env:
    notes: Provisioned non-production test account only.
targets:
  - name: protected-browser-entry
    fqdn: browser-ai-test.example.org
    allowed_ips: [203.0.113.10]
    allowed_paths: [/, /login, /upload, /assistant]
    scheme: https
    ports: [443]
    credential_ref: test-user-1
    tags: [browser-ai, menlo-style, authorized-black-box]
prohibited_actions:
  - credential theft
  - token theft
  - cookie theft
  - browser c2
  - mfa bypass
  - destructive testing
  - third-party testing outside scope
""", encoding="utf-8")
