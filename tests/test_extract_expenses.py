# Built-in imports
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local Imports
from src.textract.parse_textract_output import parse_textract_file
from src.core.extract_expenses import extract_expenses_from_tables

def main():

    # Path to previously generated Textract JSON output
    input_path = "data/textract_output/2025-07-22_1035_cb23bdf6_BC - MC - 02 - FEB-2025.pdf.json"

    if not os.path.exists(input_path):
        print(f"❌ Missing file: {input_path}")
        return

    # Parse tables
    tables = parse_textract_file(input_path)
    print(f"Parsed {len(tables)} tables from Textract output.")

    # Extract expenses using template adapter
    expenses = extract_expenses_from_tables(tables, template_name="bancolombia_v1")

    # Summary counts
    usd_count = len(expenses["usd_expenses"])
    cop_count = len(expenses["cop_expenses"])

    print(f"USD Expenses: {usd_count}")
    print(f"COP Expenses: {cop_count}")

    # Show first few records for sanity check
    print("\n--- Sample USD expense ---")
    if usd_count > 0:
        print(json.dumps(expenses["usd_expenses"][5], indent=2, ensure_ascii=False))

    print("\n--- Sample COP expense ---")
    if cop_count > 0:
        print(json.dumps(expenses["cop_expenses"][5], indent=2, ensure_ascii=False))



# Nameguard
if __name__ == "__main__":
    main() 