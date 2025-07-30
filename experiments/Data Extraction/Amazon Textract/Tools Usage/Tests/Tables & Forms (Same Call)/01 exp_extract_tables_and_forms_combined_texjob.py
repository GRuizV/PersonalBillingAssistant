"""
01 exp_extract_tables_and_forms_combined_texjob

    This experiment tries to get everything (TABLES & FORMS) from a combined textract job
    and reconstruct the whole bill in a manageable format.


"""






import boto3
import json
import time
from urllib.parse import urlparse
from typing import List, Dict, Any, Union

# ---------- Textract Call ----------

def analyze_document(s3_uri: str) -> List[Dict[str, Any]]:
    """
    Calls Textract to analyze a document using both TABLES and FORMS.
    Handles pagination for multi-page documents.
    Saves raw Textract JSON to disk.
    """
    parsed = urlparse(s3_uri)
    bucket_name = parsed.netloc
    document_name = parsed.path.lstrip("/")

    textract = boto3.client("textract", region_name="us-east-2")

    response = textract.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": bucket_name, "Name": document_name}},
        FeatureTypes=["TABLES", "FORMS"],
    )

    job_id = response["JobId"]
    print(f"Started Textract job: {job_id}")

    # Wait for completion
    status = ""
    while status not in ["SUCCEEDED", "FAILED"]:
        job_status = textract.get_document_analysis(JobId=job_id)
        status = job_status["JobStatus"]
        print(f"Job status: {status}")
        if status not in ["SUCCEEDED", "FAILED"]:
            time.sleep(3)

    if status == "FAILED":
        raise RuntimeError("Textract job failed")

    # Paginated retrieval
    pages = []
    next_token = None
    while True:
        if next_token:
            result = textract.get_document_analysis(JobId=job_id, NextToken=next_token)
        else:
            result = job_status
        pages.append(result)
        next_token = result.get("NextToken")
        if not next_token:
            break


    # Save raw JSON
    raw_json_path = r"experiments\Data Extraction\Amazon Textract\Tools Usage\Tests\Tables, Forms & Layout Parsing\01 exp output\raw_result.json"
    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    print("Raw Textract JSON saved to raw_textract_response.json")

    return pages

# ---------- Parsing helpers ----------

def extract_table(table_block: Dict[str, Any], blocks: List[Dict[str, Any]]) -> List[List[str]]:
    """Extracts table data from a Textract TABLE block."""
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
    table = []
    for r in sorted(rows.keys()):
        row = [rows[r].get(c, "") for c in sorted(rows[r].keys())]
        table.append(row)
    return table

def build_reading_order(pages: List[Dict[str, Any]]) -> List[Dict[str, Union[str, List[List[str]]]]]:
    """
    Builds reading order mixing lines and tables.
    Adds currency tagging based on 'ESTADO DE CUENTA EN:' markers.
    """
    sequence = []
    current_currency = None

    for page in pages:
        blocks = page["Blocks"]
        sorted_blocks = sorted(
            blocks,
            key=lambda b: (
                b.get("Geometry", {}).get("BoundingBox", {}).get("Top", 0),
                b.get("Geometry", {}).get("BoundingBox", {}).get("Left", 0),
            ),
        )

        for block in sorted_blocks:
            btype = block["BlockType"]

            if btype == "LINE":
                text = block["Text"].strip()
                sequence.append({"type": "line", "content": text})
                # Check for currency markers
                if "ESTADO DE CUENTA EN: DOLARES" in text.upper():
                    current_currency = "USD"
                elif "ESTADO DE CUENTA EN: PESOS" in text.upper():
                    current_currency = "COP"

            elif btype == "TABLE":
                table = extract_table(block, blocks)
                sequence.append({"type": "table", "currency": current_currency, "content": table})

    return sequence

def create_markdown(sequence: List[Dict[str, Any]], output_path: str) -> None:
    """Creates Markdown preview showing reading order and currency context."""
    md_lines = ["## Document Reading Order (With Currency Context)\n"]
    for item in sequence:
        if item["type"] == "line":
            md_lines.append(f"- [line] {item['content']}")
        elif item["type"] == "table":
            md_lines.append(f"- [table] currency={item.get('currency')}")
            for row in item["content"]:
                md_lines.append(f"  - {row}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Markdown preview saved to {output_path}")

# ---------- Main ----------

if __name__ == "__main__":
    s3_uri = "s3://textract-console-us-east-2-3fa63c34-2f89-48d5-8377-96e2f72c5853/document-uploader-1753815970254/Extracto_774507892_202501_TARJETA_MASTERCARD_3667.pdf"

    pages = analyze_document(s3_uri)
    sequence = build_reading_order(pages)

    # Save sequence JSON
    out_json = r"experiments\Data Extraction\Amazon Textract\Tools Usage\Tests\Tables, Forms & Layout Parsing\01 exp output\result.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(sequence, f, ensure_ascii=False, indent=2)
    print("Document sequence saved to document_sequence.json")

    # Save Markdown preview
    md_out_path = r"experiments\Data Extraction\Amazon Textract\Tools Usage\Tests\Tables, Forms & Layout Parsing\01 exp output\result.md"
    create_markdown(sequence, md_out_path)