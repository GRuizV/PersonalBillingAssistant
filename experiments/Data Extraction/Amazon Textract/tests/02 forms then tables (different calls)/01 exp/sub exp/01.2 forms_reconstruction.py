import json
from typing import Dict, Any, List


def load_json(path: str) -> List[Dict[str, Any]]:
    """Loads Textract raw JSON (list of pages)."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def summarize_blocks(pages: List[Dict[str, Any]]) -> Dict[str, int]:
    """Counts block types across all pages."""
    counts = {}
    for page in pages:
        for block in page["Blocks"]:
            btype = block["BlockType"]
            counts[btype] = counts.get(btype, 0) + 1
    return counts


def build_block_map(pages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Creates a global map of block Id -> block content."""
    block_map = {}
    for page in pages:
        for block in page["Blocks"]:
            block_map[block["Id"]] = block
    return block_map


def extract_key_value_pairs(block_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extracts all key-value pairs across all pages."""
    results = []
    for block in block_map.values():
        if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
            key_text = get_text(block, block_map)
            value_text = ""
            for rel in block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    for vid in rel["Ids"]:
                        value_block = block_map.get(vid)
                        if value_block:
                            value_text = get_text(value_block, block_map)
            bbox = block.get("Geometry", {}).get("BoundingBox", {})
            page_number = block.get("Page", None)
            results.append({
                "key": key_text.strip(),
                "value": value_text.strip(),
                "position": {
                    "top": bbox.get("Top", None),
                    "left": bbox.get("Left", None)
                },
                "page": page_number,
                "source": "KV"
            })
    return results


def get_text(block: Dict[str, Any], block_map: Dict[str, Dict[str, Any]]) -> str:
    """Gets text from a block by traversing its child WORD and LINE blocks."""
    text = ""
    for rel in block.get("Relationships", []):
        if rel["Type"] == "CHILD":
            for cid in rel["Ids"]:
                word = block_map.get(cid)
                if word and "Text" in word:
                    text += word["Text"] + " "
    return text.strip()


def save_json(data: Dict[str, Any], output_path: str) -> None:
    """Saves dictionary as JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON summary saved to {output_path}")


if __name__ == "__main__":

    raw_forms_path = r"experiments\data extraction\amazon textract\tests\forms then tables (different calls)\raw jsons\raw_forms.json"
    output_json  = r"experiments\data extraction\amazon textract\tests\forms then tables (different calls)\outputs\full_forms.json"

    pages = load_json(raw_forms_path)
    summary = summarize_blocks(pages)
    block_map = build_block_map(pages)
    kv_pairs = extract_key_value_pairs(block_map)
    final = {"found_pairs": kv_pairs, "summary": summary}
    save_json(final, output_json)

    print(f"Extracted {len(kv_pairs)} key-value pairs with positions and page info.")