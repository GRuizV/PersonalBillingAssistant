# Builtin Imports
import os
import json
import time

# Local Imports
...

# Third-party imports
import boto3
from dotenv import load_dotenv





# Load environment variables
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

# Init boto client
textract = boto3.client(
    "textract",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


# Main function
def run_textract_analysis(s3_key: str, save_to: str = None, poll_interval: int = 5) -> dict:
    
    """
    Asynchronously analyzes a PDF in S3 using Textract's start_document_analysis.
    Handles pagination to retrieve all blocks.
    
    Args:
        s3_key (str): The S3 object key of the PDF file.
        save_to (str): Optional. Path to save the JSON response.
        poll_interval (int): Seconds to wait between polling attempts.

    Returns:
        dict: Full Textract analysis result with all blocks.
    """

    try:
        # Start the async job
        response = textract.start_document_analysis(
            DocumentLocation={'S3Object': {'Bucket': S3_BUCKET, 'Name': s3_key}},
            FeatureTypes=["TABLES"]
        )

        job_id = response["JobId"]
        print(f"📤 Textract job started. JobId: {job_id}")


        # Poll until job finishes
        while True:
            job_status = textract.get_document_analysis(JobId=job_id)
            status = job_status["JobStatus"]

            if status == "SUCCEEDED":
                print("✅ Textract job succeeded.")
                break
            elif status == "FAILED":
                raise RuntimeError("❌ Textract job failed.")
            else:
                print(f"⏳ Job status: {status}... retrying in {poll_interval}s")
                time.sleep(poll_interval)


        # Pagination Handling         
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
            "Blocks": all_blocks,
            "DocumentMetadata": page.get("DocumentMetadata"),
            "JobStatus": "SUCCEEDED"
        }


        # Save to file if requested
        if save_to:
            os.makedirs(os.path.dirname(save_to), exist_ok=True)
            with open(save_to, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            print(f"📝 Saved Textract output to {save_to}")

        return result


    except Exception as e:
        print(f"❌ Textract async call failed: {e}")
        raise