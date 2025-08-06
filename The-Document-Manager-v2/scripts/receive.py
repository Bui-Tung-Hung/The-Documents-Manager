#!/usr/bin/env python3
"""
Example script for receiving and processing messages from SQS
"""

import boto3
import json
import asyncio
import requests
import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def process_sqs_messages():
    """Receive messages from SQS and process documents"""
    
    # Configure AWS clients for LocalStack
    sqs_client = boto3.client(
        'sqs',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test'),
        region_name='us-east-1'
    )
    
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test'),
        region_name='us-east-1'
    )
    
    queue_name = 'document-processing-queue'
    api_url = 'http://localhost:8001'
    
    # Get queue URL
    try:
        response = sqs_client.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
        print(f"✅ Connected to queue: {queue_name}")
    except Exception as e:
        print(f"❌ Error getting queue URL: {e}")
        return
    
    print("🔄 Polling for messages...")
    
    # Poll for messages
    while True:
        try:
            # Receive messages
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=5
            )
            
            messages = response.get('Messages', [])
            if not messages:
                print("⏳ No messages, continuing to poll...")
                continue
            
            for message in messages:
                try:
                    # Parse message
                    body = json.loads(message['Body'])
                    file_key = body['file_key']
                    bucket = body['bucket']
                    file_id = body['file_id']
                    metadata = body.get('metadata', {})
                    
                    print(f"📄 Processing: {file_key}")
                    
                    # Download document from S3
                    s3_response = s3_client.get_object(Bucket=bucket, Key=file_key)
                    content = s3_response['Body'].read().decode('utf-8')
                    
                    # Index document via API
                    index_request = {
                        "documents": [
                            {
                                "content": content,
                                "file_id": file_id,
                                "metadata": metadata
                            }
                        ]
                    }
                    
                    response = requests.post(
                        f"{api_url}/index-documents",
                        json=index_request,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ Indexed: {file_key} -> {file_id}")
                    else:
                        print(f"❌ Failed to index {file_key}: {response.text}")
                    
                    # Delete message from queue
                    sqs_client.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    continue
        
        except KeyboardInterrupt:
            print("\n🔄 Stopping message processing...")
            break
        except Exception as e:
            print(f"❌ Error polling messages: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("📥 Starting SQS message processor...")
    asyncio.run(process_sqs_messages())
