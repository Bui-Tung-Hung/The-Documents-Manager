import boto3

# Connect to SQS (LocalStack endpoint shown; change for real AWS)
sqs = boto3.client(
    'sqs',
    region_name='us-east-1',
    aws_access_key_id='test',              # Use your actual key for AWS
    aws_secret_access_key='test',
    endpoint_url='http://localhost:4566'   # Use this only for LocalStack
)


# Replace with your actual queue name
queue_name = 'test-queue'


# Get the queue URL
response = sqs.get_queue_url(QueueName=queue_name)
queue_url = response['QueueUrl']


# Send a message
response = sqs.send_message(
    QueueUrl=queue_url,
    MessageBody='Hello from Boto3!'
)


print("Message sent. Message ID:", response['MessageId'])
