from textractor.entities.document import Document
from textractor.data.text_extraction_result import TextractOutput
from tabulate import tabulate

# --- Configuration ---
#AVVILLAS
json_path = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\POCs\Extraccion de Data\Amazon Textract\Tools Usage\AV - VS - 03 - MAR-2025\Tables\analyzeDocResponse.json"  # <--- Change this path to your local JSON file

# --- Load Textract JSON into Textractor Document ---
doc = Document.from_document(DocumentFile.from_json(json_path))

# --- Extract Tables ---
tables = doc.tables

# --- Display Tables ---
if not tables:
    print("No tables found in the document.")

else:
    for i, table in enumerate(tables, start=1):
        print(f"\nTable {i}:\n")
        print(tabulate(table.to_str_matrix(), headers="firstrow", tablefmt="grid"))


