# Builtin Imports
import json




# Main function
def parse_textract_tables(textract_json: dict) -> list:

    """
    Parses Textract JSON output and extracts tables as 2D lists.
    
    Args:
        textract_json (dict): Raw Textract response JSON.

    Returns:
        list: A list of tables, each table is a list of rows (lists of cell values)
    """

    # JSON blocks parsing
    blocks = textract_json.get("Blocks", [])
    block_map = {b["Id"]: b for b in blocks}
    
    # Lists holder
    tables = []
    

    # JSON Traversal to get all TABLE types
    for block in blocks:

        if block["BlockType"] == "TABLE":
            
            table = []  # Really necessary?*
            
            # Collect all CELL blocks related to this TABLE
            cell_ids = []

            for rel in block.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    cell_ids.extend(rel["Ids"])
            
            cells = [block_map[cell_id] for cell_id in cell_ids if block_map[cell_id]["BlockType"] == "CELL"]
            
            # Build row/col matrix
            max_row = max(cell["RowIndex"] for cell in cells)
            max_col = max(cell["ColumnIndex"] for cell in cells)
            

            # Table reconstruction
            matrix = [["" for _ in range(max_col)] for _ in range(max_row)]
            
            for cell in cells:

                text = ""

                # Extract text from CHILD relationships (WORDS)
                for rel in cell.get("Relationships", []):
                    if rel["Type"] == "CHILD":
                        text = " ".join(block_map[wid]["Text"] for wid in rel["Ids"] if block_map[wid]["BlockType"] == "WORD")
                
                # Cell text population
                matrix[cell["RowIndex"] - 1][cell["ColumnIndex"] - 1] = text
            
            tables.append(matrix)
    
    return tables


# Function Caller
def parse_textract_file(json_file_path: str) -> list:

    """Load a Textract JSON file and parse its tables."""

    with open(json_file_path, "r", encoding="utf-8") as f:
        textract_json = json.load(f)
        
    return parse_textract_tables(textract_json)