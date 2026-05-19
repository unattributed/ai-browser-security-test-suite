# File: src/ai_browser_security_suite/config.py
# Change description: define local-first scope models for authorized browser-AI validation.
# Git commit comment: focus suite on ollama webui local target
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

    credentials = [
        CredentialRef(
            name=str(item["name"]),
            username_env=item.get("username_env"),
            password_env=item.get("password_env"),
            token_env=item.get("token_env"),
            notes=item.get("notes"),
        )
        for item in raw.get("credential_refs", [])
    ]

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
    scope_path.write_text(
        """---
client_name: local ollama webui validation
engagement_name: local browser ai target validation
authorization_reference: local-owned-target
passive_only_default: true
notes: >
  Default public workflow is the local unattributed/ollama-webui target.
  Replace this file only for explicit client-authorized engagements.
credential_refs:
  - name: local-test-user
    username_env:
    password_env:
    token_env:
    notes: Local target does not require credentials by default.
targets:
  - name: ollama-webui-local
    fqdn: 127.0.0.1
    allowed_ips: [127.0.0.1]
    allowed_paths: [/, /health, /api/tags, /api/models, /api/generate]
    scheme: http
    ports: [11435]
    credential_ref:
    tags: [ollama-webui, local-target, browser-ai, supported-default]
prohibited_actions:
  - credential theft
  - token theft
  - cookie theft
  - browser c2
  - mfa bypass
  - destructive testing
  - third-party testing outside explicit written scope
""",
        encoding="utf-8",
    )
