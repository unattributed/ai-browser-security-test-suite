from __future__ import annotations

from ai_browser_security_suite.browser_capture import _url_allowed
from ai_browser_security_suite.config import Scope, Target


def make_scope() -> Scope:
    return Scope(
        client_name="local-test",
        engagement_name="browser-capture-scope",
        authorization_reference="local-owned-target",
        passive_only_default=True,
        targets=[
            Target(
                name="loopback-target",
                fqdn="127.0.0.1",
                scheme="http",
                ports=[11435],
                allowed_paths=["/health", "/api/generate"],
            ),
            Target(
                name="localhost-target",
                fqdn="localhost",
                scheme="http",
                ports=[11435],
                allowed_paths=["/chat", "/api/models"],
            ),
        ],
    )


def test_loopback_url_is_allowed_when_host_scheme_and_path_match_scope() -> None:
    scope = make_scope()

    assert _url_allowed("http://127.0.0.1:11435/health", scope)
    assert _url_allowed("http://127.0.0.1:11435/api/generate?case=baseline", scope)


def test_localhost_url_is_allowed_when_explicitly_scoped() -> None:
    scope = make_scope()

    assert _url_allowed("http://localhost:11435/chat/session", scope)
    assert _url_allowed("http://localhost:11435/api/models", scope)


def test_external_hostname_is_denied_even_when_path_matches() -> None:
    scope = make_scope()

    assert not _url_allowed("http://example.com/health", scope)


def test_unscoped_scheme_is_denied_for_matching_loopback_host() -> None:
    scope = make_scope()

    assert not _url_allowed("https://127.0.0.1:11435/health", scope)


def test_unscoped_path_is_denied_for_matching_loopback_host() -> None:
    scope = make_scope()

    assert not _url_allowed("http://127.0.0.1:11435/admin", scope)


def test_root_allowed_path_documents_prefix_scope_behavior() -> None:
    scope = Scope(
        client_name="local-test",
        engagement_name="browser-capture-root-scope",
        authorization_reference="local-owned-target",
        passive_only_default=True,
        targets=[
            Target(
                name="loopback-root-target",
                fqdn="127.0.0.1",
                scheme="http",
                ports=[11435],
                allowed_paths=["/"],
            )
        ],
    )

    assert _url_allowed("http://127.0.0.1:11435/admin", scope)
