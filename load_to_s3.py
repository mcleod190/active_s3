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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to S3 subscription.")

    parser.add_argument(
        "--list",  
        action="store_true",
        help="list all buckets"
    )
    parser.add_argument(
        "-f", "--file", 
        help="Path to a file to be uploaded"
    )
    parser.add_argument(
        "-b", "--bucket", 
        help="bucket name"
    )

    args = parser.parse_args()
    if args.list:
        list_buckets()
    else:
        if not args.file or not args.bucket:
            parser.error("the following arguments are required when --list is not specified: --file, --bucket")

        upload_file(args.file, args.bucket)