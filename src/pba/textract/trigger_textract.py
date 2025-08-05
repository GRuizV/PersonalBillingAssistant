# Builtin Imports
import os
import json
import time

# Third-party imports
import boto3
from dotenv import load_dotenv





# Load environment variables
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

# Initialize AWS Textract client
textract = boto3.client(
    "textract",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)




# Helper Function
def _start_and_wait_textract(s3_key: str, feature_types: list, poll_interval: int = 5) -> dict:

    """
    Helper function that starts a Textract asynchronous analysis job
    for the given FeatureTypes and waits until completion.

    Args:
        s3_key (str): Key of the document in the configured S3 bucket.
        feature_types (list): List of Textract FeatureTypes, e.g., ["FORMS"] or ["TABLES"].
        poll_interval (int): Seconds to wait between status checks.

    Returns:
        dict: Combined Textract response blocks and metadata for that feature type.
    """

    # Start the Textract asynchronous job
    response = textract.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": S3_BUCKET, "Name": s3_key}},
        FeatureTypes=feature_types,
    )

    job_id = response["JobId"]
    print(f"""📤 Textract job started. Features: "{feature_types}"", JobId: {job_id}""")


    # Poll until job finishes
    while True:
        job_status = textract.get_document_analysis(JobId=job_id)
        status = job_status["JobStatus"]

        if status == "SUCCEEDED":
            print(f"✅ Textract job succeeded for {feature_types}")
            break
        elif status == "FAILED":
            raise RuntimeError(f"❌ Textract job failed for {feature_types}")
        else:
            print(f"⏳ Job status: {status}... retrying in {poll_interval}s")
            time.sleep(poll_interval)


    # Collect all pages using pagination     
    all_blocks = []
    next_token = None

    while True:
        if next_token:
            page = textract.get_document_analysis(JobId=job_id, NextToken=next_token)

        else:
            page = textract.get_document_analysis(JobId=job_id)

        all_blocks.extend(page["Blocks"])
        next_token = page.get("NextToken")

        if not next_token:
            break


    # Final combined result
    result = {
        "DocumentMetadata": page.get("DocumentMetadata"),
        "JobStatus": "SUCCEEDED",
        "FeatureTypes": feature_types,
        "Blocks": all_blocks,
    }

    return result

# Main Function
def run_dual_textract_analysis(s3_key: str, save_to: str = None, poll_interval: int = 5) -> dict:
    """
    Run two separate Textract asynchronous analysis jobs:
    1) FORMS → to extract metadata, key-value pairs, and currency markers.
    2) TABLES → to extract expense tables cleanly (avoiding corruption from mixed call).

    Results are kept separate for clarity and to support downstream logic that
    links table data with metadata (e.g., currency markers positioned relative to tables).

    Args:
        s3_key (str): Key of the document in the configured S3 bucket.
        save_to (str, optional): Local path to save the combined JSON result.
        poll_interval (int): Seconds to wait between polling attempts.

    Returns:
        dict: Unified structure containing:
            {
                "s3_source": { "bucket": <bucket>, "key": <s3_key> },
                "forms": { ...Textract FORMS output... },
                "tables": { ...Textract TABLES output... },
            }
    """
    try:
        # Run the FORMS job (metadata, currency markers)
        forms_result = _start_and_wait_textract(s3_key, ["FORMS"], poll_interval)
        print(f"DEBUG: FORMS result blocks: {None if not forms_result else len(forms_result.get('Blocks', []))}")

        # Run the TABLES job (expense tables)
        tables_result = _start_and_wait_textract(s3_key, ["TABLES"], poll_interval)
        print(f"DEBUG: TABLES result blocks: {None if not tables_result else len(tables_result.get('Blocks', []))}")

        # Combine into one unified structure (but still keep them separate)
        combined_result = {
            "s3_source": {"bucket": S3_BUCKET, "key": s3_key},
            "forms": forms_result,
            "tables": tables_result,
        }

        # Optionally save to file for debugging or offline analysis
        if save_to:
            os.makedirs(os.path.dirname(save_to), exist_ok=True)
            with open(save_to, "w", encoding="utf-8") as f:
                json.dump(combined_result, f, indent=2)
            print(f"📝 Saved dual Textract output to {save_to}")

        return combined_result

    except Exception as e:
        print(f"❌ Dual Textract analysis failed: {e}")
        raise