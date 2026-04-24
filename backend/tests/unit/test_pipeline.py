from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.models import StoredFile
from src.tasks.pipeline import MAX_FILE_SIZE_BYTES, detect_threats, extract_metadata


def make_file(**kwargs) -> StoredFile:
    defaults = {
        "id": "test-id",
        "title": "Test File",
        "original_name": "test.txt",
        "stored_name": "test-id.txt",
        "mime_type": "text/plain",
        "size": 1024,
        "processing_status": "uploaded",
    }
    defaults.update(kwargs)
    obj = MagicMock(spec=StoredFile)
    for key, value in defaults.items():
        setattr(obj, key, value)
    return obj


class TestDetectThreats:
    def test_clean_file_returns_empty_list(self):
        file = make_file(original_name="document.pdf", mime_type="application/pdf", size=1024)
        assert detect_threats(file) == []

    @pytest.mark.parametrize(
        "extension",
        [".exe", ".bat", ".cmd", ".sh", ".js", ".ps1", ".vbs", ".msi"],
    )
    def test_suspicious_extension_flagged(self, extension: str):
        file = make_file(original_name=f"malware{extension}", mime_type="application/octet-stream")
        reasons = detect_threats(file)
        assert len(reasons) == 1
        assert extension in reasons[0]

    def test_oversized_file_flagged(self):
        file = make_file(size=MAX_FILE_SIZE_BYTES + 1)
        reasons = detect_threats(file)
        assert any("size" in r for r in reasons)

    def test_file_exactly_at_limit_is_clean(self):
        file = make_file(size=MAX_FILE_SIZE_BYTES)
        reasons = detect_threats(file)
        assert not any("size" in r for r in reasons)

    def test_pdf_mime_mismatch_flagged(self):
        file = make_file(original_name="doc.pdf", mime_type="text/html")
        reasons = detect_threats(file)
        assert any("MIME" in r for r in reasons)

    def test_pdf_correct_mime_is_clean(self):
        file = make_file(original_name="doc.pdf", mime_type="application/pdf")
        reasons = detect_threats(file)
        assert not any("MIME" in r for r in reasons)

    def test_multiple_threats_accumulate(self):
        file = make_file(
            original_name="big.exe",
            mime_type="application/octet-stream",
            size=MAX_FILE_SIZE_BYTES + 1,
        )
        reasons = detect_threats(file)
        assert len(reasons) == 2

    def test_extension_case_insensitive(self):
        file = make_file(original_name="VIRUS.EXE")
        reasons = detect_threats(file)
        assert len(reasons) == 1


class TestExtractMetadata:
    def test_basic_metadata_always_present(self, tmp_path: Path):
        file_path = tmp_path / "test.txt"
        file_path.write_text("hello world")

        file = make_file(
            original_name="test.txt",
            stored_name="test.txt",
            mime_type="text/plain",
            size=11,
        )
        metadata = extract_metadata(file, file_path)

        assert metadata["extension"] == ".txt"
        assert metadata["size_bytes"] == 11
        assert metadata["mime_type"] == "text/plain"

    def test_text_file_has_line_and_char_count(self, tmp_path: Path):
        content = "line1\nline2\nline3"
        file_path = tmp_path / "test.txt"
        file_path.write_text(content)

        file = make_file(
            original_name="test.txt",
            stored_name="test.txt",
            mime_type="text/plain",
            size=len(content),
        )
        metadata = extract_metadata(file, file_path)

        assert metadata["line_count"] == 3
        assert metadata["char_count"] == len(content)

    def test_pdf_file_has_page_count(self, tmp_path: Path):
        pdf_content = b"/Type /Page some content /Type /Page more content"
        file_path = tmp_path / "doc.pdf"
        file_path.write_bytes(pdf_content)

        file = make_file(
            original_name="doc.pdf",
            stored_name="doc.pdf",
            mime_type="application/pdf",
            size=len(pdf_content),
        )
        metadata = extract_metadata(file, file_path)

        assert metadata["approx_page_count"] == 2

    def test_pdf_without_page_markers_returns_one(self, tmp_path: Path):
        file_path = tmp_path / "empty.pdf"
        file_path.write_bytes(b"%PDF-1.4")

        file = make_file(
            original_name="empty.pdf",
            stored_name="empty.pdf",
            mime_type="application/pdf",
            size=8,
        )
        metadata = extract_metadata(file, file_path)

        assert metadata["approx_page_count"] == 1

    def test_binary_file_has_no_text_metadata(self, tmp_path: Path):
        file_path = tmp_path / "image.png"
        file_path.write_bytes(b"\x89PNG\r\n\x1a\n")

        file = make_file(
            original_name="image.png",
            stored_name="image.png",
            mime_type="image/png",
            size=8,
        )
        metadata = extract_metadata(file, file_path)

        assert "line_count" not in metadata
        assert "char_count" not in metadata
        assert "approx_page_count" not in metadata
