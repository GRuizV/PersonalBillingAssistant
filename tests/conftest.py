# Bultin imports
import json
import os

# Third-party imports
import pytest

# Local imports
from src.textract.parse_textract_output import parse_textract_file




@pytest.fixture
def ground_truth_data():
    """
    Fixture: Load ground truth expense data for validation tests.

    Returns:
        dict: {
            "expenses": [  # unified expense list
                {
                    "currency": "USD" | "COP",
                    "authorization_number": str,
                    "transaction_date": str (YYYY-MM-DD),
                    "description": str,
                    "original_amount": float,
                    "charges_and_credits": float,
                    "deferred_balance": float,
                    "installments": str
                },
                ...
            ]
        }
    """
    path = os.path.join(
        os.path.dirname(__file__),
        "extraction_testing_data",
        "extraction_ground_truth.json"
    )
    if not os.path.exists(path):
        pytest.skip(f"Missing ground truth data file: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_tables():
    """
    Fixture: Load sample table data as parsed from Textract output JSON.

    Returns:
        list: List of tables (list of lists) representing one processed bill's raw table output.
    """
    path = os.path.join(
        os.path.dirname(__file__),
        "extraction_testing_data",
        "extraction_test_results",
        "extracted.json"
    )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def bancolombia_tables():

    """Fixture: Load parsed tables for a known Bancolombia CC bill (Feb 2025)."""

    input_path = "data/textract_output/2025-07-22_1035_cb23bdf6_BC - MC - 02 - FEB-2025.pdf.json"
    
    if not os.path.exists(input_path):
        pytest.skip(f"Missing input file: {input_path}")
    return parse_textract_file(input_path)
