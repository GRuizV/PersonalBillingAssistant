"""
Tests for the dual Textract analysis module (trigger_textract.py).

Fast tests use fakes from conftest.py (no AWS calls).
One optional integration test calls AWS and is marked @pytest.mark.slow.
"""


# Built-in imports
import json

# Local imports
from pba.textract.trigger_textract import run_dual_textract_analysis

# Third party import
import pytest




# ----------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------

def test_run_dual_textract_analysis_happy(patch_textract,
                                          fake_get_document_analysis_success,
                                          fake_forms_blocks,
                                          fake_tables_blocks):
    """
    Happy-path test:
    - Both FORMS and TABLES jobs succeed.
    - Ensures the returned structure has forms, tables, and s3_source keys.
    """

    # Monkeypatch injection from conftest to set the proper tested function response ready
    patch_textract(get_impl=fake_get_document_analysis_success)

    # Run analysis on a fake S3 key (no real AWS call)
    s3_key = "uploads/sample.pdf"
    result = run_dual_textract_analysis(s3_key)

    # Validate structure and content
    assert "s3_source" in result
    assert "forms" in result
    assert "tables" in result
    assert result["forms"]["Blocks"] == fake_forms_blocks
    assert result["tables"]["Blocks"] == fake_tables_blocks
    assert result["s3_source"]["key"] == s3_key


def test_run_dual_textract_analysis_saves_file(patch_textract,
                                               fake_get_document_analysis_success,
                                               tmp_path): 

    """
    Ensures that when `save_to` is provided, a JSON file is written to disk.
    """

    # Monkeypatch injection from conftest to set the proper tested function response ready
    patch_textract(get_impl=fake_get_document_analysis_success)

    # Define temporary save path (pytest tmp_path fixture provides a temp directory)
    save_path = tmp_path / "dual_result.json"

    # Run analysis and save to file
    run_dual_textract_analysis("uploads/sample.pdf", save_to=str(save_path))

    # Validate file existence and basic content
    assert save_path.exists()
    content = json.loads(save_path.read_text())
    assert "forms" in content and "tables" in content


def test_run_dual_textract_analysis_job_failure(patch_textract,
                                                fake_get_document_analysis_failed):
    
    """
    Ensures a `RuntimeError` is raised if Textract job status is FAILED.
    """

    # Monkeypatch injection from conftest to set the proper tested function response ready
    patch_textract(get_impl=fake_get_document_analysis_failed)

    # Job failure should raise RuntimeError
    with pytest.raises(RuntimeError):
        run_dual_textract_analysis("uploads/sample.pdf")


def test_run_dual_textract_analysis_pagination(patch_textract,
                                               fake_get_document_analysis_paginated,
                                               fake_forms_blocks,
                                               fake_tables_blocks):

    """
    Ensures pagination logic concatenates blocks from multiple pages.
    """

    # Monkeypatch injection from conftest to set the proper tested function response ready
    patch_textract(get_impl=fake_get_document_analysis_paginated)

    # Run analysis
    result = run_dual_textract_analysis("uploads/sample.pdf")

    # Because we simulate two pages, block counts should double
    assert len(result["forms"]["Blocks"]) == len(fake_forms_blocks) * 2
    assert len(result["tables"]["Blocks"]) == len(fake_tables_blocks) * 2


# ----------------------------------------------------------------------
# Optional Integration Test (real AWS call)
# ----------------------------------------------------------------------
@pytest.mark.slow
def test_run_dual_textract_analysis_integration(tmp_path):
    """
    Real AWS Textract integration test.

    Requirements:
    - AWS credentials configured (e.g., in .env)
    - Document already uploaded to S3 at the given key.
    - This test is marked as 'slow' and skipped by default unless explicitly enabled.

    Purpose:
    - Verify that our pipeline works end-to-end with a real Textract job.
    - Provides extra confidence beyond the mocked tests.

    Usage:
        pytest -m slow
    """
    s3_key = "uploads/Extracto_774507892_202501_TARJETA_MASTERCARD_3667.pdf"
    save_path = tmp_path / "integration_result.json"

    result = run_dual_textract_analysis(s3_key, save_to=str(save_path))

    # Validate basic structure and saved file existence
    assert "forms" in result and "tables" in result
    assert save_path.exists()
    # We don't assert block counts here because they depend on the actual document




# Manual runner
if __name__ == "__main__":

    # Example S3 key for testing (replace with a real uploaded bill path)
    s3_key = "uploads/Extracto_774507892_202501_TARJETA_MASTERCARD_3667.pdf"

    # Save results under audit folder for inspection
    save_path = r"audit\textract_output\textract_response.json"

    # Function call
    result = run_dual_textract_analysis(s3_key, save_to=save_path, poll_interval=5)

    print("\nManual run complete. Summary:")
    print(f"  Forms blocks:  {len(result['forms']['Blocks'])}")
    print(f"  Tables blocks: {len(result['tables']['Blocks'])}")
    print(f"  Output saved:  {save_path}")