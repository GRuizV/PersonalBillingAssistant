# Bultin imports
import json
from pathlib import Path

# Third-party imports
import pytest




# -----------------------------------------------------------------------------
# Shared paths (adjust if you relocate fixtures)
# -----------------------------------------------------------------------------
TEXTRACT_JSON_PATH = Path("tests/fixtures/textract_response.json")
TEMPLATE_PATH = Path("config/bill_templates.json")
TEMPLATE_NAME = "bancolombia_v1"




# -----------------------------------------------------------------------------
# Generic / cross-module fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
def sample_pdf(tmp_path):

    """
    Creates a temporary, minimal PDF-like file for tests that need a local PDF path.
    Returns a string path to avoid surprising Path/str mismatches in call sites.
    """

    pdf_dir = tmp_path
    pdf_path = pdf_dir / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    return str(pdf_path)


@pytest.fixture(scope="session")
def bill_original_name() -> str:
    """Canonical filename used across parser-related tests."""
    return "Extracto_774507892_202501_TARJETA_MASTERCARD_3667.pdf"




# -----------------------------------------------------------------------------
# Textract trigger fakes (used by trigger_textract tests)
# -----------------------------------------------------------------------------

@pytest.fixture(scope="session")
def fake_forms_blocks():
    """Minimal FORMS blocks to simulate a successful response page."""
    return [{"BlockType": "KEY_VALUE_SET", "Id": "1", "Page": 1}]


@pytest.fixture(scope="session")
def fake_tables_blocks():
    """Minimal TABLE block to simulate a successful response page."""
    return [{"BlockType": "TABLE", "Id": "2", "Page": 1}]


@pytest.fixture(scope="session")
def fake_start_document_analysis():
    """
    Fake textract.start_document_analysis that returns distinct JobIds based on FeatureTypes.
    """
    def _impl(DocumentLocation, FeatureTypes):
        if "FORMS" in FeatureTypes:
            return {"JobId": "forms-job-id"}
        if "TABLES" in FeatureTypes:
            return {"JobId": "tables-job-id"}
        raise ValueError("Unexpected FeatureTypes")
    return _impl


@pytest.fixture(scope="session")
def fake_get_document_analysis_success(fake_forms_blocks, fake_tables_blocks):
    """
    Always returns SUCCEEDED with a single page of blocks.
    """
    def _impl(JobId, NextToken=None):
        blocks = fake_forms_blocks if JobId == "forms-job-id" else fake_tables_blocks
        return {"JobStatus": "SUCCEEDED", "Blocks": blocks, "DocumentMetadata": {"Pages": 1}}
    return _impl


@pytest.fixture(scope="session")
def fake_get_document_analysis_paginated(fake_forms_blocks, fake_tables_blocks):
    """
    First call returns NextToken to simulate pagination; second call ends the stream.
    """
    def _impl(JobId, NextToken=None):
        blocks = fake_forms_blocks if JobId == "forms-job-id" else fake_tables_blocks
        if NextToken is None:
            return {
                "JobStatus": "SUCCEEDED",
                "Blocks": blocks,
                "DocumentMetadata": {"Pages": 1},
                "NextToken": "token-1",
            }
        return {"JobStatus": "SUCCEEDED", "Blocks": blocks, "DocumentMetadata": {"Pages": 1}}
    return _impl


@pytest.fixture(scope="session")
def fake_get_document_analysis_failed():
    """Always returns FAILED to exercise error handling."""
    def _impl(JobId, NextToken=None):
        return {"JobStatus": "FAILED"}
    return _impl


@pytest.fixture
def patch_textract(monkeypatch, fake_start_document_analysis):
    """
    Helper to patch both textract calls in one go.

    Usage in tests:
        patch_textract(get_impl=fake_get_document_analysis_success)
        patch_textract(get_impl=fake_get_document_analysis_paginated)
        patch_textract(get_impl=fake_get_document_analysis_failed)
    """
    def _apply(get_impl):
        monkeypatch.setattr(
            "pba.textract.trigger_textract.textract.start_document_analysis",
            fake_start_document_analysis
        )
        monkeypatch.setattr(
            "pba.textract.trigger_textract.textract.get_document_analysis",
            get_impl
        )
    return _apply



# -----------------------------------------------------------------------------
# Parser fixtures (used by parse_textract_output tests)
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def _textract_fixture_json() -> dict:
    """
    Load the frozen dual Textract response once for the session.
    Provides fast, deterministic unit tests independent of audit/.
    """
    if not TEXTRACT_JSON_PATH.exists():
        raise FileNotFoundError(
            f"Missing test fixture: {TEXTRACT_JSON_PATH} "
            f"(Did you copy a working textract_response.json into tests/fixtures/?)"
        )
    return json.loads(TEXTRACT_JSON_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def textract_forms(_textract_fixture_json) -> dict:
    """The 'forms' section from the frozen Textract fixture."""
    return _textract_fixture_json["forms"]


@pytest.fixture(scope="session")
def textract_tables(_textract_fixture_json) -> dict:
    """The 'tables' section from the frozen Textract fixture."""
    return _textract_fixture_json["tables"]


@pytest.fixture(scope="session")
def bill_template() -> dict:
    """
    Load the bancolombia_v1 template (source-of-truth config).
    Kept in config/ rather than tests/fixtures/ by design.
    """
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Missing config file: {TEMPLATE_PATH} "
            f"(Ensure you run tests from project root and the file exists.)"
        )
    data = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    try:
        return data["bill_templates"][TEMPLATE_NAME]
    except KeyError as e:
        raise KeyError(
            f"Template '{TEMPLATE_NAME}' not found in {TEMPLATE_PATH}. "
            f"Available keys: {list(data.get('bill_templates', {}).keys())}"
        ) from e
    













    