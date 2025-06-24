import datetime
import os
from typing import Optional

from google.cloud import storage
from loguru import logger


def get_storage_client(service_account_file: Optional[str] = None) -> storage.Client:
    """Get a Google Cloud Storage client, using service account file if provided."""
    if service_account_file and os.path.exists(service_account_file):
        return storage.Client.from_service_account_json(service_account_file)
    else:
        # Use default credentials (Application Default Credentials)
        return storage.Client()


def make_blob_public(bucket_name, blob_name):
    """
    Makes a specific object in a Google Cloud Storage bucket public.

    Args:
        bucket_name (str): Your bucket name (e.g. 'my-bucket').
        blob_name (str): Your object name (e.g. 'my-file.txt').
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Note: This requires the "Storage Object Admin" role on your user account.
    # It internally grants the "Storage Object Viewer" role to "allUsers".
    try:
        blob.make_public()

        print(f"Success! Object '{blob_name}' in bucket '{bucket_name}' is now publicly readable.")
        print("\nIts public URL is:")
        print(blob.public_url)
        return blob.public_url

    except Exception as e:
        print(f"An error occurred: {e}")
        print("\nPlease ensure your bucket does not have Public Access Prevention enabled.")
        print("You also need the 'Storage Object Admin' role on your account.")


def generate_signed_url(
    bucket_name: str, blob_name: str, service_account_file: Optional[str] = None, expiration_hours: int = 1
) -> Optional[str]:
    """Generates a v4 signed URL for downloading a blob.

    Args:
        bucket_name (str): Your bucket name (e.g. 'farmwise_media')
        blob_name (str): Your object name (e.g. 'images/photo.jpg')
        service_account_file (str, optional): The path to your service account key file.
        expiration_hours (int): Number of hours the URL should be valid for (default: 1)

    Returns:
        str: The signed URL, or None if there was an error.
    """
    try:
        storage_client = get_storage_client(service_account_file)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Set the expiration time for the URL
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=expiration_hours)

        # Generate the signed URL (for a GET request)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=expiration_time,
            method="GET",
        )
        logger.info(f"Successfully generated signed URL for {blob_name}")
        return signed_url

    except Exception as e:
        logger.error(f"Error generating signed URL for {blob_name}: {e}")
        return None


def upload_file_to_gcs(
    file_path: str, bucket_name: str, blob_name: str, service_account_file: Optional[str] = None
) -> bool:
    """Upload a file to Google Cloud Storage.

    Args:
        file_path (str): Local file path to upload
        bucket_name (str): GCS bucket name
        blob_name (str): Destination blob name in GCS
        service_account_file (str, optional): The path to your service account key file.

    Returns:
        bool: True if upload was successful, False otherwise.
    """
    try:
        storage_client = get_storage_client(service_account_file)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.upload_from_filename(file_path)
        logger.info(f"Successfully uploaded {file_path} to gs://{bucket_name}/{blob_name}")
        return True

    except Exception as e:
        logger.error(f"Error uploading {file_path} to GCS: {e}")
        return False


def upload_bytes_to_gcs(
    data: bytes, bucket_name: str, blob_name: str, content_type: str = None, service_account_file: Optional[str] = None
) -> bool:
    """Upload bytes data to Google Cloud Storage.

    Args:
        data (bytes): Data to upload
        bucket_name (str): GCS bucket name
        blob_name (str): Destination blob name in GCS
        content_type (str, optional): MIME type of the data
        service_account_file (str, optional): The path to your service account key file.

    Returns:
        bool: True if upload was successful, False otherwise.
    """
    try:
        storage_client = get_storage_client(service_account_file)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if content_type:
            blob.content_type = content_type

        blob.upload_from_string(data)
        logger.info(f"Successfully uploaded data to gs://{bucket_name}/{blob_name}")
        return True

    except Exception as e:
        logger.error(f"Error uploading data to GCS: {e}")
        return False
