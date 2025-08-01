import json
from typing import Dict, Any, List


def load_json(path: str) -> List[Dict[str, Any]]:
    """
    Loads a Textract raw JSON output file.

    Args:
        path (str): Path to the Textract TABLES raw JSON file.

    Returns:
        List[Dict[str, Any]]: List of page results from Textract.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_block_map(pages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Builds a global block map from Textract output.
    Required to resolve relationships between TABLE -> CELL -> WORD.

    Args:
        pages (List[Dict[str, Any]]): Textract output pages.

    Returns:
        Dict[str, Dict[str, Any]]: Map of block Id to block details.
    """
    block_map = {}
    for page in pages:
        for block in page["Blocks"]:
            block_map[block["Id"]] = block
    return block_map


def get_text(block: Dict[str, Any], block_map: Dict[str, Dict[str, Any]]) -> str:
    """
    Extracts concatenated text from a block's WORD/LINE children.

    Args:
        block (Dict[str, Any]): Textract block.
        block_map (Dict[str, Dict[str, Any]]): Global block map.

    Returns:
        str: Concatenated text content.
    """
    text = ""
    for rel in block.get("Relationships", []):
        if rel["Type"] == "CHILD":
            for cid in rel["Ids"]:
                word = block_map.get(cid)
                if word and "Text" in word:
                    text += word["Text"] + " "
    return text.strip()


def extract_table(table_block: Dict[str, Any], block_map: Dict[str, Dict[str, Any]]) -> List[List[str]]:
    """
    Reconstructs a table structure from a TABLE block.

    Args:
        table_block (Dict[str, Any]): TABLE block from Textract.
        block_map (Dict[str, Dict[str, Any]]): Global block map.

    Returns:
        List[List[str]]: Reconstructed table as a list of rows, each row is a list of strings.
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

    # Convert row dictionary into ordered list of lists
    table_data = []
    for r in sorted(rows.keys()):
        row = [rows[r].get(c, "") for c in sorted(rows[r].keys())]
        table_data.append(row)
    return table_data


def extract_all_tables(block_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts all tables from Textract output with their page number.

    Args:
        block_map (Dict[str, Dict[str, Any]]): Global block map.

    Returns:
        List[Dict[str, Any]]: List of tables with page number and content.
    """
    tables = []
    for block in block_map.values():
        if block["BlockType"] == "TABLE":
            page = block.get("Page", None)
            table_data = extract_table(block, block_map)
            tables.append({
                "page": page,
                "content": table_data
            })
    return tables


def save_json(data: Any, output_path: str):
    """
    Saves data as a JSON file.

    Args:
        data (Any): Data to save.
        output_path (str): Output file path.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Extracted tables saved to {output_path}")


# Main loop event call
if __name__ == "__main__":

    # Path to Textract TABLES raw JSON
    raw_tables_path = r"experiments\data extraction\amazon textract\tests\forms then tables (different calls)\raw jsons\raw_tables.json"
    output_json = r"experiments\data extraction\amazon textract\tests\forms then tables (different calls)\outputs\extracted_tables.json"

    # Load and process Textract TABLES output
    pages = load_json(raw_tables_path)
    block_map = build_block_map(pages)
    tables = extract_all_tables(block_map)

    # Save tables with page numbers
    save_json(tables, output_json)

    # # Printout
    # for i, tb in enumerate(tables):
        
    #     print(f'\n--- Elem {i} ---')
        
    #     for j, stb in enumerate(tb["content"]):

    #         print(f"\n ### Sub-elem {i}.{j} content###")
    #         print(stb)
        
