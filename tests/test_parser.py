# Built-in imports
import sys
import os

# Module path setting
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local imports
from src.textract.parse_textract_output import parse_textract_file


# Variables setting
tables = parse_textract_file(r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\data\textract_output\2025-07-22_1035_cb23bdf6_BC - MC - 02 - FEB-2025.pdf.json")

# Function testing
for t_idx, table in enumerate(tables):

    print(f"\n--- Table {t_idx+1} ---")

    for row in table:
        print(row)