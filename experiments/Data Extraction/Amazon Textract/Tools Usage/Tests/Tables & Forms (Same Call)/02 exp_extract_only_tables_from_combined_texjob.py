"""
02 exp_extract_only_tables_from_combined_texjob

    This experiment tries to get ONLY TABLES from a combined textract job call for "TABLES" & "FORMS".
    and reconstruct the expenses tables fully complying to the ground truth.

"""

import json
from typing import Dict, Any, List


def extract_table(table_block: Dict[str, Any], blocks: List[Dict[str, Any]]) -> List[List[str]]:

    """Reconstructs a table structure from a TABLE block using linked CELL blocks."""

    rows: Dict[int, Dict[int, str]] = {}
    for rel in table_block.get("Relationships", []):
        if rel["Type"] == "CHILD":
            for cid in rel["Ids"]:
                cell = next((b for b in blocks if b["Id"] == cid), None)
                if cell and cell["BlockType"] == "CELL":
                    row_index = cell["RowIndex"]
                    col_index = cell["ColumnIndex"]
                    text = ""
                    for rel2 in cell.get("Relationships", []):
                        if rel2["Type"] == "CHILD":
                            for cid2 in rel2["Ids"]:
                                word = next((b for b in blocks if b["Id"] == cid2), None)
                                if word and "Text" in word:
                                    text += word["Text"] + " "
                    rows.setdefault(row_index, {})[col_index] = text.strip()
                    
    # Convert dict to sorted list of rows
    table = []

    for r in sorted(rows.keys()):
        row = [rows[r].get(c, "") for c in sorted(rows[r].keys())]
        table.append(row)
    return table


def reconstruct_tables(raw_json_path: str, output_md_path: str) -> None:

    """
    Reads raw Textract JSON (list of pages) and reconstructs all tables.
    Outputs them to a Markdown file.
    """

    with open(raw_json_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    md_lines = ["## Tables Extracted from Raw JSON\n"]
    table_count = 0

    for page_num, page in enumerate(pages, start=1):
        blocks = page["Blocks"]
        for block in blocks:
            if block["BlockType"] == "TABLE":
                table_count += 1
                table = extract_table(block, blocks)
                md_lines.append(f"### Table {table_count} (Page {page_num})")
                for row in table:
                    md_lines.append(f"- {row}")
                md_lines.append("")

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"{table_count} tables extracted and saved to {output_md_path}")




# Main event loop calling
if __name__ == "__main__":
    
    raw_json_path = r"experiments\Data Extraction\Amazon Textract\Tools Usage\Tests\Tables & Forms (Same Call)\01 exp output\raw_textract_response.json"
    output_md_path = r"experiments\Data Extraction\Amazon Textract\Tools Usage\Tests\Tables & Forms (Same Call)\02 exp output\output.md"
    reconstruct_tables(raw_json_path, output_md_path)