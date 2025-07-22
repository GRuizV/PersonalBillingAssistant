# Built-in imports
import sys
import os

# Module path setting
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local imports
from src.textract.trigger_textract import run_textract_analysis


# Variables setting
s3_key = "uploads/2025-07-22_1035_cb23bdf6_BC - MC - 02 - FEB-2025.pdf"
output_file = f"data/textract_output/{os.path.basename(s3_key)}.json"

# Function testing
run_textract_analysis(s3_key, save_to=output_file)