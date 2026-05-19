from __future__ import annotations

import pytest

from ai_browser_security_suite.config import ScopeError, load_scope, write_scope_template


def test_scope_template_requires_authorization_for_active_checks(tmp_path):
    scope_path = tmp_path / "scope.yaml"
    write_scope_template(scope_path)

    scope = load_scope(scope_path)

    assert scope.targets[0].base_urls() == ["http://127.0.0.1:11435"]
    with pytest.raises(ScopeError, match="authorization"):
        scope.require_authorization(active_requested=True, authorization_flag=False)

    scope.require_authorization(active_requested=True, authorization_flag=True)


def test_load_scope_rejects_invalid_allowed_ip(tmp_path):
    scope_path = tmp_path / "scope.yaml"
    scope_path.write_text(
        """
client_name: test
engagement_name: test
authorization_reference: local
targets:
  - name: invalid
    fqdn: example.test
    allowed_ips: [not-an-ip]
""",
        encoding="utf-8",
    )

    with pytest.raises(ScopeError, match="invalid IP"):
        load_scope(scope_path)
