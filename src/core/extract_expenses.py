# Built-in imports
import os
import json
import re
from datetime import datetime




# Constants setting
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config/bill_templates.json")


# --- Auxiliar Functions ---
def load_template(template_name: str) -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        templates = json.load(f)
    return templates["bill_templates"][template_name]

def normalize_value(value: str) -> str:
    return value.strip() if isinstance(value, str) else value

def parse_amount(value: str) -> float:
    """Convert amount string to float, keeping negatives as negatives."""
    if not value:
        return 0.0
    clean = re.sub(r"[^\d,.-]", "", str(value))
    clean = clean.replace(",", "")  # handle thousand separators
    try:
        return float(clean)
    except ValueError:
        return 0.0

def parse_int(value: str) -> int:
    try:
        return int(re.sub(r"[^\d]", "", str(value))) if value else 0
    except ValueError:
        return 0

def parse_date(value: str) -> str:
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y"):
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return value.strip()

def header_matches(expected: list, actual: list) -> bool:
    """Check if actual table header contains all expected headers in order."""
    normalized_actual = [normalize_value(h).lower() for h in actual]
    normalized_expected = [h.lower() for h in expected]
    return all(h in normalized_actual for h in normalized_expected)

def classify_currency(table: list, template: dict) -> str:
    """
    Determine if table is foreign or domestic based on template currency_split rules.
    Scans rows until one matches criteria, then classifies table.
    """
    header = table[0]
    index_map = {h.lower(): idx for idx, h in enumerate(header)}

    def rule_match(row, rule):
        for col, condition in rule.items():
            col_idx = index_map.get(col.lower())
            if col_idx is None:
                return False
            value = parse_amount(row[col_idx])
            if condition == "0" and value != 0:
                return False
            if condition == "!=0" and value == 0:
                return False
        return True

    for row in table[1:]:
        if rule_match(row, template["currency_split"]["foreign"]):
            return "foreign"
        if rule_match(row, template["currency_split"]["domestic"]):
            return "domestic"
        
    return "domestic"  # default if no clear match



# --- Main Function ---

def extract_expenses_from_tables(tables: list, template_name="bancolombia_v1") -> dict:

    """
    Extract normalized expense rows from parsed tables based on template.
    Returns dict with keys 'usd_expenses' and 'cop_expenses'.
    """

    # Variables setting
    template = load_template(template_name)
    expected_headers = template["headers"]
    fields_to_extract = template["fields_to_extract"]
    exclude_descriptions = [d.upper() for d in template.get("exclude_descriptions", [])]

    
    expenses = {"usd_expenses": [], "cop_expenses": []}

    # Input traversing
    for table in tables:

        # Tables of interest guards
        if not table or len(table) < 2:
            continue

        if not header_matches(expected_headers, table[0]):
            continue

        # Build column index map
        index_map = {normalize_value(h).lower(): idx for idx, h in enumerate(table[0])}

        # Determine currency type
        currency_type = classify_currency(table, template)
        bucket = "usd_expenses" if currency_type == "foreign" else "cop_expenses"

        # Records transformation
        for row in table[1:]:

            # Skip empty rows
            if all(not c for c in row):
                continue

            # Skip excluded descriptions
            description_idx = index_map.get("descripción")
            description = normalize_value(row[description_idx]) if description_idx is not None else ""
            if description.upper() in exclude_descriptions:
                continue


            # Record holder initialized
            record = {}
            
            # Record fields traversing
            for field in fields_to_extract:

                col_idx = index_map.get(field.lower())
                value = normalize_value(row[col_idx]) if col_idx is not None and col_idx < len(row) else ""

                if "fecha" in field.lower():
                    record[field] = parse_date(value)

                elif field.lower() in ["cargos y abonos", "saldo a diferir", "valor original"]:
                    record[field] = parse_amount(value)

                else:
                    record[field] = value

            expenses[bucket].append(record)

    return expenses