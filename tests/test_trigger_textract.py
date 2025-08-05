"""
Tests for the dual Textract analysis module (trigger_textract.py).

We use `monkeypatch` to replace AWS Textract calls with fake responses:
- No external AWS calls during normal test runs.
- Ensures tests are fast, deterministic, and cost-free.

We also include one optional integration test that performs a real call to AWS Textract,
marked with `@pytest.mark.slow`. This test is skipped by default unless explicitly enabled.
"""


# Built-in imports
import sys
import os
import json
from pathlib import Path

# Local imports
from pba.textract.trigger_textract import run_dual_textract_analysis

# Third party import
import pytest



# ----------------------------------------------------------------------
# Fake AWS Responses
# These will be used to simulate Textract behavior during offline tests.
# ----------------------------------------------------------------------

# Minimal fake block outputs to simulate real Textract structures
FAKE_FORMS_BLOCKS = [{"BlockType": "KEY_VALUE_SET", "Id": "1", "Page": 1}]
FAKE_TABLES_BLOCKS = [{"BlockType": "TABLE", "Id": "2", "Page": 1}]


def fake_start_document_analysis(DocumentLocation, FeatureTypes):
    """
    Fake replacement for `textract.start_document_analysis`.

    Returns a fake JobId depending on requested FeatureTypes.
    """
    if "FORMS" in FeatureTypes:
        return {"JobId": "forms-job-id"}
    if "TABLES" in FeatureTypes:
        return {"JobId": "tables-job-id"}
    raise ValueError("Unexpected FeatureTypes")


def fake_get_document_analysis_success(JobId, NextToken=None):
    """
    Fake replacement for `textract.get_document_analysis` simulating success.
    Always returns one page of blocks and a `SUCCEEDED` status.
    """
    blocks = FAKE_FORMS_BLOCKS if JobId == "forms-job-id" else FAKE_TABLES_BLOCKS
    return {
        "JobStatus": "SUCCEEDED",
        "Blocks": blocks,
        "DocumentMetadata": {"Pages": 1},
    }


def fake_get_document_analysis_paginated(JobId, NextToken=None):
    """
    Simulates a paginated Textract response.
    - First call returns a NextToken, indicating another page.
    - Second call returns without NextToken, ending pagination.
    """
    blocks = FAKE_TABLES_BLOCKS if JobId == "tables-job-id" else FAKE_FORMS_BLOCKS

    if not NextToken:

        # First page includes NextToken to simulate multiple pages
        return {
            "JobStatus": "SUCCEEDED",
            "Blocks": blocks,
            "DocumentMetadata": {"Pages": 1},
            "NextToken": "token-1",
        }
    
    else:
        # Second page ends pagination
        return {
            "JobStatus": "SUCCEEDED",
            "Blocks": blocks,
            "DocumentMetadata": {"Pages": 1},
        }


def fake_get_document_analysis_failed(JobId, NextToken=None):
    """
    Simulates a job failure by always returning `FAILED`.
    """
    return {"JobStatus": "FAILED"}




# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_run_dual_textract_analysis_happy(monkeypatch):
    """
    Happy-path test:
    - Both FORMS and TABLES jobs succeed.
    - Ensures the returned structure has forms, tables, and s3_source keys.
    """
    
    # Patch AWS Textract client calls with fake implementations
    monkeypatch.setattr("pba.textract.trigger_textract.textract.start_document_analysis",
                        fake_start_document_analysis)
    monkeypatch.setattr("pba.textract.trigger_textract.textract.get_document_analysis",
                        fake_get_document_analysis_success)

    # Run analysis on a fake S3 key (no real AWS call)
    s3_key = "uploads/sample.pdf"
    result = run_dual_textract_analysis(s3_key)

    # Validate structure and content
    assert "s3_source" in result
    assert "forms" in result
    assert "tables" in result
    assert result["forms"]["Blocks"] == FAKE_FORMS_BLOCKS
    assert result["tables"]["Blocks"] == FAKE_TABLES_BLOCKS
    assert result["s3_source"]["key"] == s3_key


def test_run_dual_textract_analysis_saves_file(monkeypatch, tmp_path):
    """
    Ensures that when `save_to` is provided, a JSON file is written to disk.
    """

    # Patch AWS calls to return fake results
    monkeypatch.setattr("pba.textract.trigger_textract.textract.start_document_analysis",
                        fake_start_document_analysis)
    monkeypatch.setattr("pba.textract.trigger_textract.textract.get_document_analysis",
                        fake_get_document_analysis_success)

    # Define temporary save path (pytest tmp_path fixture provides a temp directory)
    save_path = tmp_path / "dual_result.json"

    # Run analysis and save to file
    run_dual_textract_analysis("uploads/sample.pdf", save_to=str(save_path))

    # Validate file existence and basic content
    assert save_path.exists()
    content = json.loads(save_path.read_text())
    assert "forms" in content and "tables" in content


def test_run_dual_textract_analysis_job_failure(monkeypatch):
    """
    Ensures a `RuntimeError` is raised if Textract job status is FAILED.
    """
    # Patch AWS calls to simulate job failure
    monkeypatch.setattr("pba.textract.trigger_textract.textract.start_document_analysis",
                        fake_start_document_analysis)
    monkeypatch.setattr("pba.textract.trigger_textract.textract.get_document_analysis",
                        fake_get_document_analysis_failed)

    # Job failure should raise RuntimeError
    with pytest.raises(RuntimeError):
        run_dual_textract_analysis("uploads/sample.pdf")


def test_run_dual_textract_analysis_pagination(monkeypatch):
    """
    Ensures pagination logic concatenates blocks from multiple pages.
    """
    # Patch AWS calls to simulate paginated responses
    monkeypatch.setattr("pba.textract.trigger_textract.textract.start_document_analysis",
                        fake_start_document_analysis)
    monkeypatch.setattr("pba.textract.trigger_textract.textract.get_document_analysis",
                        fake_get_document_analysis_paginated)

    # Run analysis
    result = run_dual_textract_analysis("uploads/sample.pdf")

    # Because we simulate two pages, block counts should double
    assert len(result["forms"]["Blocks"]) == len(FAKE_FORMS_BLOCKS) * 2
    assert len(result["tables"]["Blocks"]) == len(FAKE_TABLES_BLOCKS) * 2


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
    save_path = r"audit\textract_output\dual_textract_sample.json"

    # Function call
    result = run_dual_textract_analysis(s3_key, save_to=save_path, poll_interval=5)

    print("\nManual run complete. Summary:")
    print(f"  Forms blocks:  {len(result['forms']['Blocks'])}")
    print(f"  Tables blocks: {len(result['tables']['Blocks'])}")
    print(f"  Output saved:  {save_path}")