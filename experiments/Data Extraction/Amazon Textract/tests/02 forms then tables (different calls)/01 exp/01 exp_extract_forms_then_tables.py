"""
Unified final schema: 

{
    "bill_owner": "string | null",
    "product_id": "string | null",
    "bill_date": "string | null",
    "currency_markers": {
        "page_number": "string"
    },
    "tables": [
        {
            "page": "integer",
            "content": [
                ["string", "string", "..."],
                ["string", "string", "..."]
            ]
        }
    ]
}

"""

import json
import re
from collections import Counter
from typing import Dict, Any, List





# Regex to detect if "SEÑOR (A):" value likely contains an address
ADDRESS_PATTERN = re.compile(r"(CL|CALLE|CRA|CARRERA|AV|AVENIDA|TR|TRANSVERSAL\d{3,})", re.IGNORECASE)

# List of supported card networks
CARD_NETWORKS = ["VISA", "MASTERCARD", "AMERICAN EXPRESS", "DISCOVER"]





# -----------------------------------------------------------
# Common utilities
# -----------------------------------------------------------

def load_json(path: str) -> List[Dict[str, Any]]:
    """
    Loads Textract raw JSON output from a file.
    
    Args:
        path (str): Path to the JSON file.
    
    Returns:
        List[Dict[str, Any]]: Parsed Textract output as list of page results.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_block_map(pages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Builds a global block map (ID -> block) from Textract output.
    
    Args:
        pages (List[Dict[str, Any]]): Textract pages list.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary mapping block IDs to block content.
    """
    block_map = {}
    for page in pages:
        for block in page["Blocks"]:
            block_map[block["Id"]] = block
    return block_map

def get_text(block: Dict[str, Any], block_map: Dict[str, Dict[str, Any]]) -> str:
    """
    Extracts concatenated text from WORD/LINE children of a block.
    
    Args:
        block (Dict[str, Any]): Parent Textract block.
        block_map (Dict[str, Dict[str, Any]]): Global block map for lookup.
    
    Returns:
        str: Concatenated text string.
    """
    text = ""
    for rel in block.get("Relationships", []):
        if rel["Type"] == "CHILD":
            for cid in rel["Ids"]:
                word = block_map.get(cid)
                if word and "Text" in word:
                    text += word["Text"] + " "
    return text.strip()




# -----------------------------------------------------------
# FORMS Processing
# -----------------------------------------------------------

def choose_best_senor(values: List[str]) -> str:
    """
    Selects the best "SEÑOR (A):" value.
    Prefers entries without address-like content and picks the most frequent.
    
    Args:
        values (List[str]): All values captured for "SEÑOR (A):".
    
    Returns:
        str: Chosen bill owner name.
    """
    if not values:
        return None
    # Filter out variants containing address patterns
    name_only = [v for v in values if not ADDRESS_PATTERN.search(v)]
    if name_only:
        return Counter(name_only).most_common(1)[0][0]
    # Fallback: choose the shortest value if all have addresses
    return min(values, key=len)

def detect_card_network(block_map: Dict[str, Dict[str, Any]]) -> str:
    """
    Scans LINE and WORD blocks to detect card network names.
    Picks the most frequently occurring network (if any).
    
    Args:
        block_map (Dict[str, Dict[str, Any]]): Global block map.
    
    Returns:
        str: Card network name (e.g., "MASTERCARD"), or None if not found.
    """
    network_counter = Counter()
    for block in block_map.values():
        if block["BlockType"] in ["LINE", "WORD"] and "Text" in block:
            text = block["Text"].upper()
            for network in CARD_NETWORKS:
                if network in text:
                    network_counter[network] += 1
    return network_counter.most_common(1)[0][0] if network_counter else None

def extract_forms_data(forms_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extracts metadata from FORMS raw Textract output:
      - bill_owner ("SEÑOR (A):")
      - product_id ("TARJETA:" + detected card network)
      - bill_date ("Hasta:")
      - currency_markers (dictionary page -> marker value)
    
    Args:
        forms_pages (List[Dict[str, Any]]): Raw FORMS Textract pages.
    
    Returns:
        Dict[str, Any]: Extracted metadata.
    """
    block_map = build_block_map(forms_pages)
    senor_values = []
    tarjeta = None
    hasta = None
    currency_markers = {}

    for block in block_map.values():
        if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
            key = get_text(block, block_map)
            value = ""
            for rel in block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    for vid in rel["Ids"]:
                        value_block = block_map.get(vid)
                        if value_block:
                            value = get_text(value_block, block_map)
            page = block.get("Page", None)

            # Map keys of interest
            if key == "SEÑOR (A):":
                senor_values.append(value)
            elif key == "TARJETA:" and tarjeta is None:
                tarjeta = value
            elif key == "Hasta:" and hasta is None:
                hasta = value
            elif key == "ESTADO DE CUENTA EN:":
                currency_markers[str(page)] = value

    bill_owner = choose_best_senor(senor_values)
    network = detect_card_network(block_map)
    product_id = f"{network} {tarjeta}" if network and tarjeta else tarjeta

    return {
        "bill_owner": bill_owner,
        "product_id": product_id,
        "bill_date": hasta,
        "currency_markers": currency_markers
    }




# -----------------------------------------------------------
# TABLES Processing
# -----------------------------------------------------------

def extract_table(table_block: Dict[str, Any], block_map: Dict[str, Dict[str, Any]]) -> List[List[str]]:
    """
    Reconstructs a table from a TABLE block using its CELL children.
    
    Args:
        table_block (Dict[str, Any]): A TABLE block from Textract.
        block_map (Dict[str, Dict[str, Any]]): Global block map.
    
    Returns:
        List[List[str]]: Table as list of rows, each a list of strings.
    """
    rows = {}
    for rel in table_block.get("Relationships", []):
        if rel["Type"] == "CHILD":
            for cell_id in rel["Ids"]:
                cell = block_map.get(cell_id)
                if cell and cell["BlockType"] == "CELL":
                    row_index = cell["RowIndex"]
                    col_index = cell["ColumnIndex"]
                    cell_text = get_text(cell, block_map)
                    rows.setdefault(row_index, {})[col_index] = cell_text
    # Convert to ordered list of rows
    return [[rows[r].get(c, "") for c in sorted(rows[r].keys())] for r in sorted(rows.keys())]

def extract_tables_data(tables_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts all tables from TABLES raw Textract output.
    
    Args:
        tables_pages (List[Dict[str, Any]]): Raw TABLES Textract pages.
    
    Returns:
        List[Dict[str, Any]]: List of tables with page numbers and content.
    """
    block_map = build_block_map(tables_pages)
    tables = []
    for block in block_map.values():
        if block["BlockType"] == "TABLE":
            page = block.get("Page", None)
            table_data = extract_table(block, block_map)
            tables.append({"page": page, "content": table_data})
    return tables




# -----------------------------------------------------------
# Unified Payload
# -----------------------------------------------------------

def build_unified_payload(forms_json_path: str, tables_json_path: str) -> Dict[str, Any]:
    """
    Combines FORMS and TABLES raw Textract outputs into one unified payload.
    
    Args:
        forms_json_path (str): Path to raw FORMS Textract JSON.
        tables_json_path (str): Path to raw TABLES Textract JSON.
    
    Returns:
        Dict[str, Any]: Unified payload following final schema.
    """
    forms_pages = load_json(forms_json_path)
    tables_pages = load_json(tables_json_path)

    forms_data = extract_forms_data(forms_pages)
    tables_data = extract_tables_data(tables_pages)

    return {
        "bill_owner": forms_data["bill_owner"],
        "product_id": forms_data["product_id"],
        "bill_date": forms_data["bill_date"],
        "currency_markers": forms_data["currency_markers"],
        "tables": tables_data
    }

def save_json(data: Dict[str, Any], output_path: str):
    """
    Saves a dictionary as JSON file.
    
    Args:
        data (Dict[str, Any]): Data to save.
        output_path (str): Path to output JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Unified payload saved to {output_path}")




# -----------------------------------------------------------
# Main
# -----------------------------------------------------------
if __name__ == "__main__":

    forms_json_path = r"experiments\data extraction\amazon textract\tests\02 forms then tables (different calls)\raw jsons\raw_forms.json"   # raw FORMS Textract job JSON
    tables_json_path = r"experiments\data extraction\amazon textract\tests\02 forms then tables (different calls)\raw jsons\raw_tables.json" # raw TABLES Textract job JSON
    output_path = r"experiments\data extraction\amazon textract\tests\02 forms then tables (different calls)\outputs\final\unified_bill_payload.json"

    unified_payload = build_unified_payload(forms_json_path, tables_json_path)
    save_json(unified_payload, output_path)