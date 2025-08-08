# Builtin Imports
import json
import re
from collections import Counter
from typing import Dict, List, Any




# Constants and Patterns
ADDRESS_PATTERN = re.compile(r"(CL|CALLE|CRA|CARRERA|AV|AVENIDA|TR|TRANSVERSAL|\d{3,})", re.IGNORECASE)
CARD_NETWORKS = ["VISA", "MASTERCARD", "AMERICAN EXPRESS", "DISCOVER"]




# HELPER FUNCTIONS

# Helper: Build block map
def _build_block_map(blocks: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:

    """
    Builds a dictionary mapping block Ids to block content.
    
    Args:
        blocks (List[dict]): Textract blocks list.

    Returns:
        Dict[str, dict]: Map of block_id -> block
    """

    return {block["Id"]: block for block in blocks}


# Helper: Extract text from child WORD blocks
def _get_text_from_relationships(block: Dict[str, Any], block_map: Dict[str, Dict[str, Any]]) -> str:
    
    """
    Reconstructs text for a Textract block using its child WORD blocks.
    
    Args:
        block (dict): Textract block containing Relationships.
        block_map (dict): Map of block ids to block content.

    Returns:
        str: Concatenated text of all child WORD blocks.
    """

    # Text holder
    text_chunks = []

    # Childs Traversing
    for rel in block.get("Relationships", []):

        if rel["Type"] == "CHILD":

            for child_id in rel["Ids"]:

                word_block = block_map[child_id]

                if word_block["BlockType"] == "WORD":
                    text_chunks.append(word_block.get("Text", ""))

    # Return formed text
    return " ".join(text_chunks)


def _choose_best_senor(values: List[str]) -> str:
    
    """
    Selects the best "SEÑOR (A):" value.
    Prefers entries without address-like content and picks the most frequent.
    
    Args:
        values (List[str]): All values captured for "SEÑOR (A):".
    
    Returns:
        str: Chosen bill owner name.
    """

    if not values:
        return ""
    
    name_only = [v for v in values if not ADDRESS_PATTERN.search(v)]
    
    if name_only:
        return Counter(name_only).most_common(1)[0][0]
    
    return min(values, key=len)


def _detect_card_network(block_map: Dict[str, Dict[str, Any]]) -> str:
   
    """
    Scans LINE and WORD blocks to detect card network names.
    Picks the most frequently occurring network (if any).
    
    Args:
        block_map (Dict[str, Dict[str, Any]]): Global block map.
    
    Returns:
        str: Card network name (e.g., "MASTERCARD"), or None if not found.
    """

    counter = Counter()

    for block in block_map.values():
        if block["BlockType"] in ["LINE", "WORD"] and "Text" in block:
            text = block["Text"].upper()
            for net in CARD_NETWORKS:
                if net in text:
                    counter[net] += 1
    return counter.most_common(1)[0][0] if counter else None




# MAIN FUNCTIONS

# FORMS Parsing
def parse_forms(textract_forms_json: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
    
    """
    Parses FORMS Textract output to extract:
      - bill_owner (filtered 'SEÑOR (A):')
      - product_id (TARJETA + network)
      - bill_date
      - currency_markers (page-wise)

    Applies key remapping defined in the template's `forms_to_extract`.

    Returns:
        Dict with metadata fields.

    """

    # Parser elements set up
    forms_to_extract = template.get("forms_to_extract", {})
    blocks = textract_forms_json.get("Blocks", [])
    block_map = _build_block_map(blocks)

    # Track extracted values
    senor_values = []
    tarjeta_val = None
    bill_date_val = None
    currency_markers = {}

    # Build key-value pairs (Textract KEY_VALUE_SET)
    key_map = {}
    value_map = {}

    for block in blocks:
        if block["BlockType"] == "KEY_VALUE_SET":

            if "KEY" in block.get("EntityTypes", []):
                key_map[block["Id"]] = block
            elif "VALUE" in block.get("EntityTypes", []):
                value_map[block["Id"]] = block

    # Data parsing
    for key_id, key_block in key_map.items():
        key_text = _get_text_from_relationships(key_block, block_map)
        page = key_block.get("Page", 1)
        value_text = ""

        for rel in key_block.get("Relationships", []):
            if rel["Type"] == "VALUE":
                for value_id in rel["Ids"]:
                    value_block = value_map.get(value_id)
                    if value_block:
                        value_text = _get_text_from_relationships(value_block, block_map)

        # Match against template keys
        if key_text == forms_to_extract.get("bill_owner"):
            senor_values.append(value_text)

        elif key_text == forms_to_extract.get("product_id") and not tarjeta_val:
            tarjeta_val = value_text
            
        elif key_text == forms_to_extract.get("bill_date") and not bill_date_val:
            bill_date_val = value_text

        elif key_text == forms_to_extract.get("currency_markers"):
            currency_markers[str(page)] = value_text

    # Heuristic processing
    best_owner = _choose_best_senor(senor_values)
    card_network = _detect_card_network(block_map)
    full_product_id = f"{card_network} {tarjeta_val}" if card_network and tarjeta_val else tarjeta_val

    # Payload return
    return {
        "bill_owner": best_owner,
        "product_id": full_product_id,
        "bill_date": bill_date_val,
        "currency_markers": currency_markers
    }


# TABLES Parsing
def parse_tables(textract_tables_json: Dict[str, Any]) -> List[Dict[str, Any]]:

    """
    Parses Textract TABLES output and reconstructs tables per page.

    Args:
        textract_tables_json (dict): Textract TABLES job JSON output.

    Returns:
        list: 
            [
                {"page": page_num, "content": [["row1col1", "row1col2", ...], ...]},
                ...
            ]
    """

    # Parser elements set up
    blocks = textract_tables_json.get("Blocks", [])
    block_map = _build_block_map(blocks)

    # Tables holder
    tables_with_pages = []

    # Tables persing
    for block in blocks:

        if block["BlockType"] == "TABLE":

            page_num = block.get("Page", 1)

            # Collect CELL blocks for this table
            cell_ids = []
            for rel in block.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    cell_ids.extend(rel["Ids"])

            cells = [
                block_map[cell_id]
                for cell_id in cell_ids
                if block_map[cell_id]["BlockType"] == "CELL"
            ]

            if not cells:
                continue

            # Determine matrix size
            max_row = max(cell["RowIndex"] for cell in cells)
            max_col = max(cell["ColumnIndex"] for cell in cells)
            matrix = [["" for _ in range(max_col)] for _ in range(max_row)]

            # Populate matrix
            for cell in cells:
                text = _get_text_from_relationships(cell, block_map)
                matrix[cell["RowIndex"] - 1][cell["ColumnIndex"] - 1] = text

            tables_with_pages.append({"page": page_num, "content": matrix})

    return tables_with_pages


# Unified Parser
def parse_textract_output(forms_json: Dict[str, Any],
                          tables_json: Dict[str, Any],
                          template: Dict[str, Any],
                          bill_original_name: str) -> Dict[str, Any]:
    
    """
    Builds a unified structured payload from FORMS and TABLES Textract outputs.

    Args:
        forms_json (dict): Textract FORMS output JSON.
        tables_json (dict): Textract TABLES output JSON.
        template (dict): Template dict (with forms_to_extract & tables_extraction).
        bill_original_name (str): Original PDF filename (for traceability).

    Returns:
        dict:
            {
                "bill_original_name": "...",
                "bill_owner": "...",
                "product_id": "...",
                "bill_date": "...",
                "currency_markers": {page_num: "USD"|"COP"|...},
                "tables": [{"page": n, "content": [[...],[...]]}, ...]
            }
    """

    # Extract metadata from forms
    forms_data = parse_forms(forms_json, template)

    # Extract tables
    tables_data = parse_tables(tables_json)

    # Merge into unified payload
    unified_payload = {
        "bill_original_name": bill_original_name,
        **forms_data,
        "tables": tables_data,
    }

    return unified_payload















#--------------------------------------------
# OLDER VERSION
#--------------------------------------------

# # Main function
# def parse_textract_tables(textract_json: dict) -> list:

#     """
#     Parses Textract JSON output and extracts tables as 2D lists.
    
#     Args:
#         textract_json (dict): Raw Textract response JSON.

#     Returns:
#         list: A list of tables, each table is a list of rows (lists of cell values)
#     """

#     # JSON blocks parsing
#     blocks = textract_json.get("Blocks", [])
#     block_map = {b["Id"]: b for b in blocks}
    
#     # Lists holder
#     tables = []
    

#     # JSON Traversal to get all TABLE types
#     for block in blocks:

#         if block["BlockType"] == "TABLE":
            
#             # Collect all CELL blocks related to this TABLE
#             cell_ids = []

#             for rel in block.get("Relationships", []):
#                 if rel["Type"] == "CHILD":
#                     cell_ids.extend(rel["Ids"])
            
#             cells = [block_map[cell_id] for cell_id in cell_ids if block_map[cell_id]["BlockType"] == "CELL"]
            
#             # Build row/col matrix
#             max_row = max(cell["RowIndex"] for cell in cells)
#             max_col = max(cell["ColumnIndex"] for cell in cells)
            

#             # Table reconstruction
#             matrix = [["" for _ in range(max_col)] for _ in range(max_row)]
            
#             for cell in cells:

#                 text = ""

#                 # Extract text from CHILD relationships (WORDS)
#                 for rel in cell.get("Relationships", []):
#                     if rel["Type"] == "CHILD":
#                         text = " ".join(block_map[wid]["Text"] for wid in rel["Ids"] if block_map[wid]["BlockType"] == "WORD")
                
#                 # Cell text population
#                 matrix[cell["RowIndex"] - 1][cell["ColumnIndex"] - 1] = text
            
#             tables.append(matrix)
    
#     return tables

# # Function Caller
# def parse_textract_file(json_file_path: str) -> list:

    """Load a Textract JSON file and parse its tables."""

    with open(json_file_path, "r", encoding="utf-8") as f:
        textract_json = json.load(f)
        
    return parse_textract_tables(textract_json)