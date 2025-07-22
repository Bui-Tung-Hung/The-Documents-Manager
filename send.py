import boto3
import config


# Connect to SQS (LocalStack endpoint shown; change for real AWS)
sqs = boto3.client(
    'sqs',
    region_name=config.region_name,
    aws_access_key_id=config.aws_access_key_id,              # Use your actual key for AWS
    aws_secret_access_key=config.aws_secret_access_key,
    endpoint_url=config.endpoint_url  # Use this only for LocalStack
)

# Replace with your actual queue name
queue_name = config.queue_name


# Get the queue URL
response = sqs.create_queue(QueueName=queue_name)
queue_url = response['QueueUrl']


# Send a message
response = sqs.send_message(
    QueueUrl=queue_url,
    MessageBody='{"S3_KEY": "123456", "file_id": "default_file_id"}'  # Example message body,
)


print("Message sent. Message ID:", response['MessageId'])
