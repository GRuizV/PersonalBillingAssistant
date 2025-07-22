# Built-in imports
import sys
import os

# Module path setting
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local imports
from src.ingestion.upload_to_s3 import upload_file




# Function testing
upload_file(r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\data\input_pdfs\Bancolombia\MC\BC - MC - 02 - FEB-2025.pdf")

