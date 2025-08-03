import boto3
import config
# For LocalStack
s3 = boto3.client(
    's3',
    region_name=config.region_name,
    aws_access_key_id=config.aws_access_key_id,              # Use your actual key for AWS
    aws_secret_access_key=config.aws_secret_access_key,
    endpoint_url=config.endpoint_url  # Use this only for LocalStack
)

# Your bucket and file details
bucket_name = 'bibox-bucket'
file_path = '/home/hung/projects/Data/AttentionIsAllYouNeed.pdf'              # local file path
s3_key = '123456'         # key in S3 bucket

# Create bucket (only once, skip if already exists)
try:
    s3.create_bucket(Bucket=bucket_name)
except s3.exceptions.BucketAlreadyOwnedByYou:
    pass

# Upload file
s3.upload_file(file_path, bucket_name, s3_key)

print(f"Uploaded {file_path} to s3://{bucket_name}/{s3_key}")
