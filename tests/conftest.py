# Bultin imports
import json
import os

# Third-party imports
import pytest




@pytest.fixture
def ground_truth_data():
    """
    Fixture: Load ground truth expense data used for validating extracted results.

    Returns:
        dict: Parsed JSON object containing manually verified ground truth data 
              for one or more credit card bills.
    """
    path = os.path.join(
        os.path.dirname(__file__),
        "extraction_testing_data",
        "extraction_ground_truth.json"
    )
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