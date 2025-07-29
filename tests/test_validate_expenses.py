"""
Validation test for expense extraction results against ground truth.

This script supports two modes:
1. Manual run (for quick debugging)
2. Pytest integration (automated testing)
"""


# Built-in imports
import json
import os
import sys

# Third-party imports
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local Imports
from src.textract.parse_textract_output import parse_textract_file
from src.core.extract_expenses import extract_expenses_from_tables



"""
METRICS DEFINITION

    For each bucket (usd_expenses, cop_expenses):

        Precision: Of all extracted records, how many match ground truth exactly?
        precision = true_positives / (true_positives + false_positives)

        Recall: Of all ground truth records, how many were correctly captured?
        recall = true_positives / (true_positives + false_negatives)

    Here:

        * True positive = record index exists in both sets and all fields match.
        * False positive = record exists in extracted but not in ground truth (extra rows or mismatched fields).
        * False negative = record missing from extracted but present in ground truth.

        We'll measure on index-aligned records (like unit tests) but also handle count differences.

"""

# --- Helper Funcs ---
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def record_key(record):
    """
    Build a unique key for an expense record based on stable identifying fields.
    This helps compare extracted vs ground truth without depending on row order.
    """
    return (
        record.get("authorization_number", "").strip(),
        record.get("transaction_date", "").strip(),
        str(record.get("original_amount", "")).strip(),
        record.get("currency", "").strip()
    )

def compare_records(extracted, ground_truth):
    """
    Compare expenses ignoring order, using composite key match.
    
    Returns:
        mismatches: list of (record_key, field_differences)
        tp: number of true positives
        fp: number of false positives
        fn: number of false negatives
    """
    extracted_map = {record_key(e): e for e in extracted}
    ground_map = {record_key(g): g for g in ground_truth}

    mismatches = []
    true_positives = 0

    for key, g in ground_map.items():

        e = extracted_map.get(key)

        if not e:
            continue

        row_mismatch = []

        for field in g.keys():

            if str(e.get(field, "")).strip() != str(g.get(field, "")).strip():
                row_mismatch.append((field, e.get(field), g.get(field)))

        if row_mismatch:
            mismatches.append((key, row_mismatch))
        else:
            true_positives += 1

    false_positives = len(set(extracted_map.keys()) - set(ground_map.keys()))
    false_negatives = len(set(ground_map.keys()) - set(extracted_map.keys()))

    return mismatches, true_positives, false_positives, false_negatives

def validate_expenses(extracted, ground_truth):
    """
    Validate all extracted expenses against ground truth.
    Prints precision, recall, and mismatch summary.
    """
    mismatches, tp, fp, fn = compare_records(extracted, ground_truth)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    print(f"Extracted: {len(extracted)}, Ground truth: {len(ground_truth)}")
    print(f"True Positives: {tp}, False Positives: {fp}, False Negatives: {fn}")
    print(f"Precision: {precision:.2%}, Recall: {recall:.2%}")

    if mismatches:
        print(f"❌ {len(mismatches)} row mismatches found (field differences):")
        for key, diffs in mismatches[:10]:
            print(f"  Record Key: {key}")
            for field, val_e, val_g in diffs:
                print(f"    Field '{field}': extracted='{val_e}' vs ground='{val_g}'")
    else:
        print("✅ All compared rows match exactly.")




# --- Pytest test ---
@pytest.mark.parametrize("template_name", ["bancolombia_v1"])
def test_expense_validation(template_name, bancolombia_tables, ground_truth_data):
    
    """
    Pytest test:
    - Extract expenses
    - Compare against ground truth unified format
    - Fail if mismatches or record counts differ
    """

    result = extract_expenses_from_tables(bancolombia_tables, template_name=template_name)
    extracted = result.get("expenses", [])
    ground = ground_truth_data.get("expenses", [])

    mismatches, tp, fp, fn = compare_records(extracted, ground)

    assert len(set(map(record_key, extracted))) == len(extracted), "Duplicate keys in extracted data"
    assert len(set(map(record_key, ground))) == len(ground), "Duplicate keys in ground truth"

    assert fp == 0, f"Found {fp} false positives (extra records)"
    assert fn == 0, f"Found {fn} false negatives (missing records)"
    assert not mismatches, f"Found {len(mismatches)} mismatches in matched records"




# --- Manual runner ---
if __name__ == "__main__":

    # Input/Output paths
    textract_path = "data/textract_output/2025-07-22_1035_cb23bdf6_BC - MC - 02 - FEB-2025.pdf.json"
    ground_path = "tests/extraction_testing_data/extraction_ground_truth.json"
    

    # Generate extracted expenses
    tables = parse_textract_file(textract_path)
    extracted = extract_expenses_from_tables(tables, template_name="bancolombia_v1").get("expenses", [])

    # Save the resulted transformed data from the extration
    output_path = r"tests\extraction_testing_data\extraction_test_results\extracted.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)

    # Compare with ground truth
    ground = load_json(ground_path).get("expenses", [])

    # Main loop call
    validate_expenses(extracted, ground)




