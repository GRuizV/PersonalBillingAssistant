"""
integration test for upload_to_s3 module.

Verifies:
- upload_file() uploads a PDF to the configured S3 bucket.
- Confirms the file exists in the bucket after upload.
"""


# Built-in imports
import sys
import os

# Local imports
from pba.ingestion.upload_to_s3 import upload_file

# Third-party imports
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError




# Load environment variables
load_dotenv()

# Get credentials from .env
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)




# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_upload_new_file(sample_pdf, monkeypatch):
    """
    Upload a file that doesn't exist in S3 and confirm upload occurs
    under the specified test prefix.
    """

    # Sample definition
    prefix = "test_uploads"
    s3_key = f"{prefix}/sample.pdf"

    # Remove file from S3 if exists
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
    except ClientError:
        pass

    # Call upload_file with test-specific prefix
    result = upload_file(sample_pdf, prefix=prefix)

    # Assert the file retrieved by the function is the same set initially
    assert result == "sample.pdf"

    # Verify file exists in S3 under test prefix
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix + "/")
    assert "Contents" in response
    assert any(obj["Key"] == s3_key for obj in response["Contents"])


def test_upload_duplicate_ignore(sample_pdf, monkeypatch):
    """
    Upload a duplicate and choose to ignore.
    """

    # Sample definition
    prefix = "test_uploads"
    s3_key = f"{prefix}/sample.pdf"

    # Ensure file already exists in S3 first
    s3_client.upload_file(sample_pdf, S3_BUCKET, s3_key)

    # Simulate user choosing "ignore"
    monkeypatch.setattr("builtins.input", lambda _: "ignore")

    # Call upload_file (should detect duplicate and skip)
    result = upload_file(sample_pdf, prefix=prefix)

     # Assert the file retrieved by the function is the same set initially
    assert result == "sample.pdf"

    # Confirm object still exists (implicitly unchanged)
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix + "/")
    assert "Contents" in response
    assert any(obj["Key"] == s3_key for obj in response["Contents"])


def test_upload_duplicate_replace(sample_pdf, monkeypatch):
    """
    Upload a duplicate file and choose to replace it.
    """

    # Sample definition
    prefix = "test_uploads"
    s3_key = f"{prefix}/sample.pdf"

    # Ensure file already exists in S3 first
    s3_client.upload_file(sample_pdf, S3_BUCKET, s3_key)

    # Simulate user choosing "replace"
    monkeypatch.setattr("builtins.input", lambda _: "replace")

    # Call upload_file (should detect duplicate and overwrite)
    result = upload_file(sample_pdf, prefix=prefix)

     # Assert the file retrieved by the function is the same set initially
    assert result == "sample.pdf"

    # Confirm object still exists after replacement
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix + "/")
    assert "Contents" in response
    assert any(obj["Key"] == s3_key for obj in response["Contents"])




# Manual runner
if __name__ == "__main__":
    
    """
    Manual run to verify upload works end-to-end.
    Adjust file_path to point to a real PDF before running.
    """

    file_path = r"data\input_pdfs\Bancolombia\MC\Extracto_774507892_202501_TARJETA_MASTERCARD_3667.pdf"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    uploaded_name = upload_file(file_path)
    print(f"Manual test complete. Uploaded: {uploaded_name}")
