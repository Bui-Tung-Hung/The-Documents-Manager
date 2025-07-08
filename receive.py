import boto3

# Connect to LocalStack
sqs = boto3.client(
    'sqs',
    region_name='us-east-1',
    aws_access_key_id='test',             # dummy for LocalStack
    aws_secret_access_key='test',         # dummy for LocalStack
    endpoint_url='http://localhost:4566'  # LocalStack endpoint
)

# Replace with your existing queue name
queue_name = 'test-queue'

# Get the queue URL
response = sqs.get_queue_url(QueueName=queue_name)
queue_url = response['QueueUrl']

# Receive message
while 1:
    message_response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5  # Enable long polling
    )

    messages = message_response.get('Messages', [])
    for msg in messages:
        print("Message Body:", msg['Body'])
        print("Receipt Handle:", msg['ReceiptHandle'])

        # Delete the message after processing (optional)
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg['ReceiptHandle']
        )
