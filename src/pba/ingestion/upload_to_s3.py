# Builtin Imports
import os
import uuid
from datetime import datetime

# Local Imports
...

# Third-party imports
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv




# Load environment variables
load_dotenv()

# Get credentials from .env
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


# Main function
def upload_file(file_path: str, prefix: str = "uploads") -> str:

    """
    Uploads a file to the configured S3 bucket.

    Args:
        file_path (str): local path to the PDF.
        prefix (str, optional): S3 key prefix. Defaults to "uploads".

    Returns:
        str: original filename of the uploaded PDF.
    """

    # File existance guard
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")    


    # Original bill name getting
    bill_original_name = os.path.basename(file_path)


    # Check if file already exists in S3
    s3_key = f"{prefix}/{bill_original_name}"

    try:

        # S3 object calling
        s3.head_object(Bucket=S3_BUCKET, Key=s3_key)

        # If no exception, file exists
        choice = input(
            f"File '{bill_original_name}' already exists in '{prefix}'. "
            "Type 'replace' to overwrite or 'ignore' to skip: "
        ).strip().lower()
        
        if choice == "ignore":
            print("Upload skipped by user decision.")
            return bill_original_name
        
        elif choice != "replace":
            raise ValueError("Invalid choice. Expected 'replace' or 'ignore'.")
    
    except ClientError as e:
    
        if e.response["Error"]["Code"] != "404":
            raise  # re-raise unexpected errors


    # Proceed to upload (new file or replace)
    try:
        s3.upload_file(file_path, S3_BUCKET, s3_key)
        print(f"✅ Uploaded '{bill_original_name}' to '{prefix}/' in bucket '{S3_BUCKET}'")
        return bill_original_name
    
    except Exception as e:
        print(f"❌ Failed to upload: {e}")
        raise