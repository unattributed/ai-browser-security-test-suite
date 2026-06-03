from __future__ import annotations

import tarfile
from pathlib import Path

PRIVATE_NAMES = {
    "mitmproxy-ca.pem",
    "mitmproxy-ca-cert.pem",
    "mitmproxy-ca-cert.cer",
    "mitmproxy-ca-cert.p12",
    "mitmproxy-ca.p12",
}


def is_private_proxy_material(path: Path) -> bool:
    lowered = path.name.lower()
    return lowered in PRIVATE_NAMES or lowered.endswith(".p12")


def remove_private_proxy_material(root: Path) -> list[Path]:
    removed: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and is_private_proxy_material(path):
            removed.append(path.relative_to(root))
            path.unlink()
    return removed


def archive_contains_private_proxy_material(archive_path: Path) -> list[str]:
    matches: list[str] = []
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            if is_private_proxy_material(Path(member.name)):
                matches.append(member.name)
    return matches


def test_private_proxy_material_cleanup_removes_representative_files(tmp_path: Path) -> None:
    live_output = tmp_path / "lab-11-live-output"
    live_output.mkdir()
    private_files = [
        live_output / "mitmproxy-ca.pem",
        live_output / "mitmproxy-ca-cert.pem",
        live_output / "mitmproxy-ca-cert.cer",
        live_output / "mitmproxy-ca-cert.p12",
        live_output / "mitmproxy-ca.p12",
        live_output / "nested" / "student-export.p12",
    ]
    public_file = live_output / "flow-summary.json"
    for path in private_files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("private material placeholder", encoding="utf-8")
    public_file.write_text("{}\n", encoding="utf-8")

    removed = remove_private_proxy_material(live_output)

    assert {path.as_posix() for path in removed} == {
        "mitmproxy-ca.pem",
        "mitmproxy-ca-cert.pem",
        "mitmproxy-ca-cert.cer",
        "mitmproxy-ca-cert.p12",
        "mitmproxy-ca.p12",
        "nested/student-export.p12",
    }
    assert public_file.exists()
    for path in private_files:
        assert not path.exists(), f"private proxy material was not removed: {path}"


def test_archive_hygiene_detects_private_proxy_material(tmp_path: Path) -> None:
    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "manifest.json").write_text("{}\n", encoding="utf-8")
    (payload / "mitmproxy-ca.p12").write_text("private material placeholder", encoding="utf-8")
    archive_path = tmp_path / "evidence.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(payload, arcname="payload")

    matches = archive_contains_private_proxy_material(archive_path)

    assert matches == ["payload/mitmproxy-ca.p12"]
