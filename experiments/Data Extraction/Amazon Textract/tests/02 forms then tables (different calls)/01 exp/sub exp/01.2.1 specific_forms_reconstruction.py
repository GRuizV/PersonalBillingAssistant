import json
import re
from collections import Counter
from typing import Dict, Any, List


# Regex to detect if a "SEÑOR (A):" value likely contains an address.
# (matches street abbreviations, numbers with 3+ digits, etc.)
ADDRESS_PATTERN = re.compile(r"(CL|CALLE|CRA|CARRERA|AV|AVENIDA|TR|TRANSVERSAL\d{3,})", re.IGNORECASE)

# List of supported card networks
CARD_NETWORKS = ["VISA", "MASTERCARD", "AMERICAN EXPRESS", "DISCOVER"]



def load_json(path: str) -> List[Dict[str, Any]]:
    """Loads a Textract raw JSON output file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_block_map(pages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Builds a global block map from Textract output."""
    block_map = {}
    for page in pages:
        for block in page["Blocks"]:
            block_map[block["Id"]] = block
    return block_map

def get_text(block: Dict[str, Any], block_map: Dict[str, Dict[str, Any]]) -> str:
    """Extracts concatenated text from a block's WORD/LINE children."""
    text = ""
    for rel in block.get("Relationships", []):
        if rel["Type"] == "CHILD":
            for cid in rel["Ids"]:
                word = block_map.get(cid)
                if word and "Text" in word:
                    text += word["Text"] + " "
    return text.strip()

def choose_best_senor(values: List[str]) -> str:
    """
    Selects the best candidate for "SEÑOR (A):".
    Prefers entries without address-like patterns and picks the most frequent one.
    """
    if not values:
        return None
    name_only = [v for v in values if not ADDRESS_PATTERN.search(v)]
    if name_only:
        return Counter(name_only).most_common(1)[0][0]
    return min(values, key=len)

def detect_card_network(block_map: Dict[str, Dict[str, Any]]) -> str:
    """
    Scans all LINE and WORD blocks for known card networks and returns the most frequent one.
    Returns None if no network is found.
    """
    network_counter = Counter()
    for block in block_map.values():
        if block["BlockType"] in ["LINE", "WORD"] and "Text" in block:
            text = block["Text"].upper()
            for network in CARD_NETWORKS:
                if network in text:
                    network_counter[network] += 1

    if network_counter:
        return network_counter.most_common(1)[0][0]
    return None

def extract_filtered_data(block_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extracts required key-value pairs and card network:
    - bill_owner ("SEÑOR (A):")
    - product_id ("TARJETA:" + network fallback)
    - bill_date ("Hasta:")
    - currency_markers ("ESTADO DE CUENTA EN:") as dictionary of {"page":"USD|COP"}
    """
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

            if key == "SEÑOR (A):":
                senor_values.append(value)
            elif key == "TARJETA:" and tarjeta is None:
                tarjeta = value
            elif key == "Hasta:" and hasta is None:
                hasta = value
            elif key == "ESTADO DE CUENTA EN:":
                # Use page number as key
                currency_markers[str(page)] = value

    # Select best bill owner
    bill_owner = choose_best_senor(senor_values)

    # Detect card network
    network = detect_card_network(block_map)

    # Append card network to product_id if found
    product_id = f"{network} {tarjeta}" if network and tarjeta else tarjeta

    return {
        "bill_owner": bill_owner,
        "product_id": product_id,
        "bill_date": hasta,
        "currency_markers": currency_markers
    }

def save_json(data: Dict[str, Any], output_path: str):
    """Saves the final metadata JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Filtered metadata saved to {output_path}")




# Main loop event call
if __name__ == "__main__":


    raw_forms_path = r"experiments\data extraction\amazon textract\tests\forms then tables (different calls)\raw jsons\raw_forms.json"
    output_json  = r"experiments\data extraction\amazon textract\tests\forms then tables (different calls)\outputs\specific_forms.json"

    pages = load_json(raw_forms_path)
    block_map = build_block_map(pages)
    metadata = extract_filtered_data(block_map)
    save_json(metadata, output_json)