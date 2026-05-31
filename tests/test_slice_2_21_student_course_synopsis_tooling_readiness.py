#!/usr/bin/env python3
"""Validate Slice 2.21 student course synopsis and tooling readiness docs."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    full_path = REPO_ROOT / path
    assert full_path.is_file(), f"missing file: {path}"
    return full_path.read_text(encoding="utf-8")


def assert_contains(path: str, terms: list[str]) -> None:
    text = read(path)
    for term in terms:
        assert term in text, f"{path} missing {term!r}"


def test_student_course_synopsis_covers_full_lab_track() -> None:
    synopsis = read("docs/workshop/student-course-synopsis.md")
    for lab_number in range(13):
        assert f"Lab {lab_number:02d}" in synopsis, f"missing Lab {lab_number:02d}"
    assert "optional Burp Suite manual proxy path" in synopsis
    assert "qrencode" in synopsis
    assert "zbarimg or zbar-tools" in synopsis
    assert "ImageMagick" in synopsis
    assert "Tesseract OCR" in synopsis
    assert "student interactive action" in synopsis.lower()
    assert "capstone attack chain" in synopsis.lower()


def test_associated_documents_reference_synopsis_and_tooling() -> None:
    assert_contains(
        "docs/workshop/README.md",
        [
            "docs/workshop/student-course-synopsis.md",
            "Student-facing course synopsis",
            "optional Burp Suite manual proxy path",
        ],
    )
    assert_contains(
        "docs/workshop/tooling-baseline.md",
        [
            "Slice 2.21 full-course student readiness tools",
            "qrencode",
            "zbarimg or zbar-tools",
            "ImageMagick",
            "Tesseract OCR",
            "optional Burp Suite manual proxy path",
        ],
    )
    assert_contains(
        "docs/workshop/provisioning-model.md",
        [
            "Slice 2.21 student course readiness provisioning contract",
            "self-hosted Debian-family Linux laptop",
            "prepared VirtualBox workshop VM",
            "media and QR authoring readiness",
        ],
    )
    assert_contains(
        "docs/lab-track-coverage-matrix.md",
        [
            "Slice 2.21 student course synopsis and tooling readiness",
            "student interactive action",
            "optional Burp Suite manual proxy path",
        ],
    )


def test_lab00_promotes_full_workshop_tooling_gate() -> None:
    assert_contains(
        "docs/workshop/labs/lab-00-environment-and-target-setup.md",
        [
            "Full-workshop tooling readiness gate",
            "media-authoring-readiness.json",
            "qrencode",
            "zbarimg or zbar-tools",
            "optional Burp Suite manual proxy path",
            "ready for Lab 01",
        ],
    )


if __name__ == "__main__":
    test_student_course_synopsis_covers_full_lab_track()
    test_associated_documents_reference_synopsis_and_tooling()
    test_lab00_promotes_full_workshop_tooling_gate()
    print("[ok] Slice 2.21 student course synopsis docs validated")
