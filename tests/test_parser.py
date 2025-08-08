"""
Manual test runner for `parse_textract_output.py`.

Loads FORMS and TABLES Textract responses from disk,
uses a real template, and prints a summary of the parsed result.
"""

# Built-in imports
import json
from pathlib import Path

# Local imports
from pba.textract.parse_textract_output import parse_textract_output




# Simulated file name for traceability
BILL_ORIGINAL_NAME = "Extracto_774507892_202501_TARJETA_MASTERCARD_3667.pdf"


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------.

def test_output_structure(textract_forms, textract_tables, bill_template):
    """
    Asserts that the unified output contains all required top-level fields.
    """
    result = parse_textract_output(
        forms_json=textract_forms,
        tables_json=textract_tables,
        template=bill_template,
        bill_original_name=BILL_ORIGINAL_NAME
    )

    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "bill_original_name",
        "bill_owner",
        "product_id",
        "bill_date",
        "currency_markers",
        "tables"
    }


def test_metadata_fields_not_empty(textract_forms, textract_tables, bill_template):
    """
    Asserts that bill_owner, product_id, bill_date are non-empty strings.
    """
    result = parse_textract_output(
        textract_forms, textract_tables, bill_template, BILL_ORIGINAL_NAME
    )

    assert isinstance(result["bill_owner"], str) and result["bill_owner"]
    assert isinstance(result["product_id"], str) and result["product_id"]
    assert isinstance(result["bill_date"], str) and result["bill_date"]


def test_currency_markers_valid(textract_forms, textract_tables, bill_template):
    """
    Validates currency_markers is a dict of str → str (e.g., "1" → "USD").
    """
    result = parse_textract_output(
        textract_forms, textract_tables, bill_template, BILL_ORIGINAL_NAME
    )

    markers = result["currency_markers"]
    assert isinstance(markers, dict)
    assert all(isinstance(k, str) for k in markers.keys())
    assert all(isinstance(v, str) for v in markers.values())


def test_tables_structure(textract_forms, textract_tables, bill_template):
    """
    Checks that tables is a non-empty list of pages with content as 2D matrices.
    """
    result = parse_textract_output(
        textract_forms, textract_tables, bill_template, BILL_ORIGINAL_NAME
    )

    tables = result["tables"]
    assert isinstance(tables, list)
    assert len(tables) > 0

    for table in tables:
        assert isinstance(table, dict)
        assert "page" in table and isinstance(table["page"], int)
        assert "content" in table and isinstance(table["content"], list)

        for row in table["content"]:
            assert isinstance(row, list)  # 2D matrix







# Manual runner
if __name__ == "__main__":

    # Paths to shared test inputs
    TEXTRACT_JSON_PATH = Path("audit/textract_output/textract_response.json")
    TEMPLATE_PATH = Path("config/bill_templates.json")
    TEMPLATE_NAME = "bancolombia_v1"
    OUTPUT_PATH = Path("audit/parsed_output/unified_payload.json")

    # Files Loading
    def textract_forms() -> dict:
        """
        Loads the 'forms' section from the dual Textract response.
        Used as input for FORMS parsing tests.
        """
        with open(TEXTRACT_JSON_PATH, encoding="utf-8") as f:
            return json.load(f)["forms"]
    def textract_tables() -> dict:
        """
        Loads the 'tables' section from the dual Textract response.
        Used as input for TABLES parsing tests.
        """
        with open(TEXTRACT_JSON_PATH, encoding="utf-8") as f:
            return json.load(f)["tables"]
    def bill_template() -> dict:
        """
        Loads the bancolombia_v1 template from the config file.
        Used by both FORMS and TABLES parsing logic.
        """
        with open(TEMPLATE_PATH, encoding="utf-8") as f:
            return json.load(f)["bill_templates"][TEMPLATE_NAME]
    
    # Function Call
    result = parse_textract_output(
        forms_json=textract_forms(),
        tables_json=textract_tables(),
        template=bill_template(),
        bill_original_name=BILL_ORIGINAL_NAME
    )
    
    # File dumping
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📝 Saved dual Textract output to {OUTPUT_PATH}")

    # Print summary
    print("✅ Parsed successfully!")
    print("Bill Owner      →", result["bill_owner"])
    print("Product ID      →", result["product_id"])
    print("Bill Date       →", result["bill_date"])
    print("Pages w/ Tables →", len(result["tables"]))
    print("Currency Map    →", result["currency_markers"])
    print("Saved to        →", OUTPUT_PATH)