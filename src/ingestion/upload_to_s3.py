# Builtin Imports
import os
import uuid
from datetime import datetime


# Local Imports
...

# Third-party imports
import boto3
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

def upload_file(file_path: str, s3_key: str = None) -> str:

    """
    Uploads a file to the configured S3 bucket.

    Args:
        file_path (str): Local path to the file.
        s3_key (str): Optional. S3 key to use (default: basename of file_path)

    Returns:
        str: S3 object key used.
    """

    if not s3_key:

        # Generate a key like: uploads/2025-07-21_1630_<UUID>.pdf
        basename = os.path.basename(file_path)
        date_prefix = datetime.now().strftime("%Y-%m-%d_%H%M")
        unique_id = str(uuid.uuid4())[:8]  # shorter UUID
        s3_key = f"uploads/{date_prefix}_{unique_id}_{basename}"

        
    try:
        s3.upload_file(file_path, S3_BUCKET, s3_key)
        print(f"✅ Uploaded '{basename}'\nLocation: to S3 bucket '{S3_BUCKET}'\nAs: '{s3_key}'")
        return s3_key
    
    except Exception as e:
        print(f"❌ Failed to upload: {e}")
        raise