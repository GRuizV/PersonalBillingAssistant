# Built-in imports
import json
import os
import sys

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

# --- Aux Funcs ---
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def compare_records(extracted, ground_truth):

    """Compare records row by row (aligned by index)."""

    mismatches = []
    true_positives = 0
    min_len = min(len(extracted), len(ground_truth))

    for i in range(min_len):

        e = extracted[i]
        g = ground_truth[i]
        row_mismatch = []

        for field in g.keys():

            if str(e.get(field, "")).strip() != str(g.get(field, "")).strip():
                row_mismatch.append((field, e.get(field), g.get(field)))

        if row_mismatch:
            mismatches.append((i, row_mismatch))
        
        else:
            true_positives += 1

    # Count differences from length mismatches
    false_positives = max(0, len(extracted) - len(ground_truth))
    false_negatives = max(0, len(ground_truth) - len(extracted))

    return mismatches, true_positives, false_positives, false_negatives

def validate_bucket(bucket, extracted, ground_truth):

    print(f"\n=== {bucket.upper()} ===")

    mismatches, tp, fp, fn = compare_records(extracted, ground_truth)

    # Precision & Recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    print(f"Extracted: {len(extracted)}, Ground truth: {len(ground_truth)}")
    print(f"True Positives: {tp}, False Positives: {fp}, False Negatives: {fn}")
    print(f"Precision: {precision:.2%}, Recall: {recall:.2%}")


    if mismatches:

        print(f"❌ {len(mismatches)} row mismatches found (field differences):")

        for idx, diffs in mismatches[:10]:  # show first 10 mismatched rows

            print(f"  Row {idx}:")

            for field, val_e, val_g in diffs:
                print(f"    Field '{field}': extracted='{val_e}' vs ground='{val_g}'")
   
    else:
        print("✅ All compared rows match exactly.")


# --- Main Testing Func ---
def main():

    # Input/Output paths
    textract_path = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\data\textract_output\2025-07-22_1035_cb23bdf6_BC - MC - 02 - FEB-2025.pdf.json"
    ground_path = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\tests\extraction_testing_data\extraction_ground_truth.json"
    

    # Generate extracted expenses
    tables = parse_textract_file(textract_path)
    extracted = extract_expenses_from_tables(tables, template_name="bancolombia_v1")

    # Save the resulted transformed data from the extration
    output_path = "tests\extraction_testing_data\extraction_test_results\extracted.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)

    # Compare with ground truth
    ground = load_json(ground_path)
    for bucket in ["usd_expenses", "cop_expenses"]:
        validate_bucket(bucket, extracted.get(bucket, []), ground.get(bucket, []))




# Nameguard
if __name__ == "__main__":
    main()