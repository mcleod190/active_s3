import os
import logging
import argparse
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError


load_dotenv()


def upload_file(file_path, bucket_name):
    session = boto3.session.Session()
    s3 = session.client(service_name = 's3',
        endpoint_url = os.getenv('ENDPOINT_URL'),
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    try:
        s3.upload_file(file_path, bucket_name, file_path)
        print(f"Successfully uploaded {file_path} to {bucket_name}")
        return True
    except ClientError as e:
        logging.error(e)
        return False
    
def download_from_ceph(bucket_name, object_name, destination=None):
    if destination is None:
        destination = os.path.basename(object_name)
    session = boto3.session.Session()
    s3 = session.client(service_name = 's3',
        endpoint_url = os.getenv('ENDPOINT_URL'),
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        )    
    try:
        s3.download_file(bucket_name, object_name, destination)
        print(f"Downloaded '{object_name}' from '{bucket_name}' to '{destination}'")
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print(f"Error: File '{object_name}' does not exist in bucket '{bucket_name}'.")
        else:
            print(f"Download failed: {e}")

def list_buckets():
    session = boto3.session.Session()
    s3 = session.client(service_name = 's3',
        endpoint_url = os.getenv('ENDPOINT_URL'),
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    try:
        response = s3.list_buckets()
        print("Existing buckets:")
        for bucket in response.get('Buckets', []):
            print(f"  - {bucket['Name']} (Created: {bucket['CreationDate']})")
    except ClientError as e:
        logging.error(e)
import boto3
from botocore.exceptions import ClientError

def list_files_in_bucket(bucket_name, prefix=""):
    session = boto3.session.Session()
    s3_client = session.client(service_name = 's3',
        endpoint_url = os.getenv('ENDPOINT_URL'),
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    paginator = s3_client.get_paginator("list_objects_v2")
    
    try:
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        file_count = 0

        for page in pages:
            # 'Contents' is omitted if the bucket or prefix is empty
            for obj in page.get("Contents", []):
                key = obj["Key"]
                size_kb = obj["Size"] / 1024
                modified = obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
                print(f"{modified} | {size_kb:8.2f} KB | {key}")
                file_count += 1

        if file_count == 0:
            print(f"No files found in bucket '{bucket_name}'.")
        else:
            print(f"\nTotal files: {file_count}")

    except ClientError as e:
        print(f"Failed to list files in '{bucket_name}': {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to S3 subscription.")

    parser.add_argument("-l", "--list",  action="store_true", help="list all buckets")
    parser.add_argument("--list-files", action="store_true", help="List files inside a specific bucket")
    parser.add_argument("-d", "--download", action="store_true", help="Download a file instead of uploading")

    parser.add_argument("-f", "--filename", help="Local path (for upload) or remote object key (for download)")
    parser.add_argument("-b", "--bucket", help="bucket name")
    parser.add_argument("-o", "--output", help="Optional local destination path when downloading")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-p", "--prefix", default="", help="Filter listed files by folder/prefix")

    args = parser.parse_args()
    if args.list:
        list_buckets()
    elif args.list_files:
        if not args.bucket:
            parser.error("--bucket is required when using --list-files")
        list_files_in_bucket(args.bucket, args.prefix)
    elif args.download:
        if not args.filename or not args.bucket:
            parser.error("--filename and --bucket are required when using --download")
        download_from_ceph(args.bucket, args.filename, args.output)   
    else:
        if not args.filename or not args.bucket:
            parser.error("the following arguments are required when --list is not specified: --file, --bucket")
        upload_file(args.filename, args.bucket)