"""
Integration test for upload_to_s3 module.

Verifies:
- upload_file() uploads a PDF to the configured S3 bucket.
- Confirms the file exists in the bucket after upload.
"""



# Built-in imports
import sys
import os

# Module path setting
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local imports
from src.ingestion.upload_to_s3 import upload_file


# Third-party imports
import pytest
import boto3



# Load bucket name from environment or config
BUCKET_NAME = os.environ.get("S3_BUCKET")

def test_upload_file_and_check_s3():

    """Upload file to S3 and verify existence."""

    # Path to a known PDF in your repo (adjust path if needed)
    file_path = os.path.join("data", "input_pdfs", "Bancolombia", "MC", "BC - MC - 01 - ENE-2025.pdf")

    # Generate unique S3 key to avoid collision
    s3_key = f"test_upload/{os.path.basename(file_path)}"
    
    # Upload file
    upload_file(file_path, s3_key)

    # Check if object exists in S3
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=s3_key)
    keys = [obj["Key"] for obj in response.get("Contents", [])] if "Contents" in response else []

    assert s3_key in keys, f"Uploaded file {s3_key} not found in S3 bucket {BUCKET_NAME}"


# Manual runner
if __name__ == "__main__":

    file_path = os.path.join("data", "input_pdfs", "Bancolombia", "MC", "BC - MC - 01 - ENE-2025.pdf")
    s3_key = f"manual_test/{os.path.basename(file_path)}"

    print(f"Uploading {file_path} to {s3_key}")
    upload_file(file_path, s3_key)
    print("Manual upload completed. Check S3 bucket for confirmation.")
