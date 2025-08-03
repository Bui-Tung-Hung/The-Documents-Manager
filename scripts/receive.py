import boto3
import config
import json
from loader import S3DocumentLoader
# Connect to LocalStack
sqs = boto3.client(
    'sqs',
    region_name=config.region_name,  # Use your actual region
    aws_access_key_id=config.aws_access_key_id,             # dummy for LocalStack
    aws_secret_access_key=config.aws_secret_access_key,         # dummy for LocalStack
    endpoint_url=config.endpoint_url  # LocalStack endpoint
)

# Replace with your existing queue name
queue_name = config.queue_name

# Get the queue URL
response = sqs.get_queue_url(QueueName=queue_name)
queue_url = response['QueueUrl']


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
    # sqs.delete_message(
    #     QueueUrl=queue_url,
    #     ReceiptHandle=msg['ReceiptHandle']
    # )

query = msg['Body']
query = json.loads(query)  # Assuming the message body is a JSON string
print("Query:", query)
print("S3 Key:", query.get('S3_KEY'))
print("File ID:", query.get('file_id'))
print("Type of query:", type(query))


if __name__ == "__main__":
    loader = S3DocumentLoader(bucket="bibox-bucket", key=query.get("S3_KEY"), fileID=query.get('file_id'))
    docs = loader.get()
    a = 0
    for doc in docs:
        print("Document Metadata:", doc.metadata)
        print("Document Content:", doc.page_content[:100], "...")
        print("-" * 80)
        print()
        a += 1
        if a==5:
            break