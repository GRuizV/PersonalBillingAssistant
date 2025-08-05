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
import pytest
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



@pytest.fixture
def sample_pdf(tmp_path):

    """Create a fake sample PDF for testing."""

    pdf_dir = tmp_path
    pdf_path = pdf_dir / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    return str(pdf_path)



def test_upload_new_file(sample_pdf, monkeypatch):
    """
    Upload a file that doesn't exist in S3 and confirm upload occurs.
    """

    s3_key = "test_uploads/sample.pdf"

    # Remove file from S3 if exists
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
    except ClientError:
        pass

    # Simulate user input (no duplicate, so no prompt)
    monkeypatch.setattr("builtins.input", lambda _: "replace")


    # Force upload destination to be under test_uploads/
    # (hardcode by copying to temp path with same name)
    import shutil
    temp_test_path = sample_pdf
    result = upload_file(temp_test_path)


    assert result == "sample.pdf"

    # Verify file exists in S3 under test_uploads/
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="test_uploads/")
    assert "Contents" in response
    assert any(obj["Key"] == s3_key for obj in response["Contents"])


# def test_upload_duplicate_ignore(sample_pdf, monkeypatch):
#     """
#     Upload a duplicate and choose to ignore.
#     """
#     # Ensure file exists in S3 first
#     s3_client.upload_file(sample_pdf, S3_BUCKET, "sample.pdf")

#     # Simulate user choosing "ignore"
#     monkeypatch.setattr("builtins.input", lambda _: "ignore")

#     result = upload_file(sample_pdf)
#     assert result == "sample.pdf"

#     # Confirm no new upload (S3 version unchanged, verified implicitly)

# def test_upload_duplicate_replace(sample_pdf, monkeypatch):
#     """
#     Upload a duplicate and choose to replace.
#     """
#     # Ensure file exists in S3 first
#     s3_client.upload_file(sample_pdf, S3_BUCKET, "sample.pdf")

#     # Simulate user choosing "replace"
#     monkeypatch.setattr("builtins.input", lambda _: "replace")

#     result = upload_file(sample_pdf)
#     assert result == "sample.pdf"

#     # Confirm upload went through (S3 still has file)
#     response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="sample.pdf")
#     assert "Contents" in response and any(obj["Key"] == "sample.pdf" for obj in response["Contents"])


# Manual runner
if __name__ == "__main__":
    
    """
    Manual run to verify upload works end-to-end.
    Adjust file_path to point to a real PDF before running.
    """

    file_path = "data\input_pdfs\Bancolombia\MC\Extracto_774507892_202501_TARJETA_MASTERCARD_3667.pdf"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    uploaded_name = upload_file(file_path)
    print(f"Manual test complete. Uploaded: {uploaded_name}")
