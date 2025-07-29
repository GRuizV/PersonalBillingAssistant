"""
Tests for extract_expenses module.
Verifies unified expense structure and expected record counts.
"""


#Builtin imports
import sys
import os

# Third party imports
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local Imports
from src.core.extract_expenses import extract_expenses_from_tables



# Variables setting
EXPECTED_USD_COUNT = 20
EXPECTED_COP_COUNT = 69

def test_expense_extraction_counts(bancolombia_tables):

    """Ensure expense extraction returns expected counts by currency."""

    result = extract_expenses_from_tables(bancolombia_tables, template_name="bancolombia_v1")
    expenses = result.get("expenses", [])
    assert isinstance(expenses, list), "Expenses output should be a list"

    # Separate by currency
    usd_expenses = [e for e in expenses if e.get("currency") == "USD"]
    cop_expenses = [e for e in expenses if e.get("currency") == "COP"]

    assert len(usd_expenses) == EXPECTED_USD_COUNT, f"Expected {EXPECTED_USD_COUNT} USD expenses"
    assert len(cop_expenses) == EXPECTED_COP_COUNT, f"Expected {EXPECTED_COP_COUNT} COP expenses"


# Manual runner for quick standalone execution
if __name__ == "__main__":

    # Local imports
    from src.textract.parse_textract_output import parse_textract_file

    input_path = "data/textract_output/2025-07-22_1035_cb23bdf6_BC - MC - 02 - FEB-2025.pdf.json"
    
    if not os.path.exists(input_path):
        print(f"❌ Missing file: {input_path}")
        
    else:

        tables = parse_textract_file(input_path)
        result = extract_expenses_from_tables(tables, template_name="bancolombia_v1")
        expenses = result.get("expenses", [])

        print(f"Total expenses: {len(expenses)}")
        print(f"USD expenses: {len([e for e in expenses if e['currency'] == 'USD'])}")
        print(f"COP expenses: {len([e for e in expenses if e['currency'] == 'COP'])}")