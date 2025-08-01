import boto3
import json
import time
from urllib.parse import urlparse
from typing import List, Dict, Any


def start_textract_job(s3_uri: str, feature_types: List[str]) -> str:
    """
    Starts a Textract asynchronous job.
    
    Args:
        s3_uri (str): S3 URI of the PDF document (e.g., s3://bucket/path/document.pdf)
        feature_types (List[str]): Textract features to use (["FORMS"] or ["TABLES"])
    
    Returns:
        str: JobId of the Textract analysis job.
    """
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    document = parsed.path.lstrip("/")

    textract = boto3.client("textract", region_name="us-east-2")

    response = textract.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": bucket, "Name": document}},
        FeatureTypes=feature_types,
    )
    return response["JobId"]


def get_textract_job_results(job_id: str) -> List[Dict[str, Any]]:
    """
    Polls Textract until the job is complete and retrieves paginated results.
    
    Args:
        job_id (str): Textract job ID.
    
    Returns:
        List[Dict[str, Any]]: List of page results.
    """
    textract = boto3.client("textract", region_name="us-east-2")
    pages = []
    next_token = None

    while True:
        if next_token:
            response = textract.get_document_analysis(JobId=job_id, NextToken=next_token)
        else:
            response = textract.get_document_analysis(JobId=job_id)
        status = response["JobStatus"]

        if status == "IN_PROGRESS":
            time.sleep(3)
            continue
        elif status == "FAILED":
            raise RuntimeError("Textract job failed.")

        pages.append(response)
        next_token = response.get("NextToken")
        if not next_token:
            break

    return pages


def save_json(data: Any, filename: str) -> None:
    """Saves Python object as JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":

    # <<< SET YOUR S3 URI HERE >>>
    s3_uri = "s3://textract-console-us-east-2-3fa63c34-2f89-48d5-8377-96e2f72c5853/document-uploader-1753815970254/Extracto_774507892_202501_TARJETA_MASTERCARD_3667.pdf"

    # --- FORMS JOB ---
    print("Starting FORMS job...")
    forms_job_id = start_textract_job(s3_uri, ["FORMS"])
    forms_results = get_textract_job_results(forms_job_id)
    out_path = r"experiments\data extraction\amazon textract\tests\forms then tables (different calls)\raw jsons\raw_forms.json"
    save_json(forms_results, out_path)
    print("FORMS raw JSON saved to textract_forms_raw.json")

    # --- TABLES JOB ---
    print("Starting TABLES job...")
    tables_job_id = start_textract_job(s3_uri, ["TABLES"])
    tables_results = get_textract_job_results(tables_job_id)
    out_path = r"experiments\data extraction\amazon textract\tests\forms then tables (different calls)\raw jsons\raw_tables.json"
    save_json(tables_results, out_path)
    print("TABLES raw JSON saved to textract_tables_raw.json")