from qdrant_manager import QdrantManager
from loader import S3DocumentLoader
import config
import boto3
import json

sqs = boto3.client(
    'sqs',
    region_name=config.region_name,  # Use your actual region
    aws_access_key_id=config.aws_access_key_id,             # dummy for LocalStack
    aws_secret_access_key=config.aws_secret_access_key,         # dummy for LocalStack
    endpoint_url=config.endpoint_url  # LocalStack endpoint
)
queue_name = config.queue_name
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
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=msg['ReceiptHandle']
    )

query = msg['Body']
query = json.loads(query)  # Assuming the message body is a JSON string


key = query.get('S3_KEY')
file_id = query.get('file_id')



if __name__ == "__main__":
    loader = S3DocumentLoader(
        bucket="bibox-bucket",
        key=key,
        fileID=file_id)
    
    docs = loader.get()  # tải tài liệu từ S3

    manager = QdrantManager(
        collection_name="TestCollection6",
        embedding_model="bge-m3:latest",
        url=config.url,
        api_key=config.api_key,
    )

    vectorstore = manager.init()        # luôn trả về vectorstore

    manager.add_documents(docs)             # thêm tài liệu
    vs = manager.get_vectorstore()      # lấy lại nếu cần
    print("Vectorstore ready with documents:", vs)
