import json
import pandas as pd
from collections import defaultdict
from pathlib import Path
from tabulate import tabulate

# Function wrapper
def pdf_extract():

    # Load the Textract JSON file
    
    # AVVILLAS
    # json_path = Path(r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\POCs\Extraccion de Data\Amazon Textract\Tools Usage\AV - VS - 03 - MAR-2025\Tables\analyzeDocResponse.json")
    
    # BANCOLOMBIA
    json_path = Path(r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\POCs\Extraccion de Data\Amazon Textract\Tools Usage\BC - MC - 01 - ENE-2025\Tables\analyzeDocResponse.json")
    
    with open(json_path, "r", encoding="utf-8") as file:
        textract_data = json.load(file)

    # Build block map for fast access
    blocks = textract_data["Blocks"]
    block_map = {block["Id"]: block for block in blocks}

    # Function to extract text from relationships
    def extract_text_from_relationships(relationships):
    
        text = ""

        for rel in relationships:
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    
                    word = block_map.get(child_id)

                    if word and word["BlockType"] == "WORD":
                        text += word["Text"] + " "

        return text.strip()


    # Process each TABLE block
    tables_data = []

    for block in blocks:

        if block["BlockType"] == "TABLE":

            table = defaultdict(lambda: defaultdict(str))

            for rel in block.get("Relationships", []):

                if rel["Type"] == "CHILD":

                    for cell_id in rel["Ids"]:

                        cell = block_map[cell_id]

                        if cell["BlockType"] == "CELL":

                            row_idx = cell["RowIndex"]
                            col_idx = cell["ColumnIndex"]
                            cell_text = extract_text_from_relationships(cell.get("Relationships", []))
                            table[row_idx][col_idx] = cell_text
        
            # Convert to 2D list
            max_col = max(max(row.keys()) for row in table.values())
            rows = []

            for i in sorted(table.keys()):
                row = [table[i].get(j, "") for j in range(1, max_col + 1)]
                rows.append(row)

            tables_data.append(rows)


    # Present tables to user
    table_dfs = [pd.DataFrame(table) for table in tables_data if table]
    # print(table_dfs)


    "TABLES DISPLAY"

    # FULL BASIC DISPLAY
    # print(table_dfs)

    # DISPLAY BY TABLE
    # for table in table_dfs:
    #     print(table)

    # TABLE OF INTEREST DISPLAY
    # print(table_dfs[3])

    # PRETTY PRINT DIPLAY
    for idx, table in enumerate(table_dfs):
        print(f"\n--- Table {idx+1} ---\n")
        print(tabulate(table, headers="keys", tablefmt="psql", showindex=False))

# Main event loop
pdf_extract()



