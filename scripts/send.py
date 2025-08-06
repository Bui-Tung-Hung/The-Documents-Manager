#!/usr/bin/env python3
"""
Example script for sending messages to SQS (LocalStack simulation)
"""

import boto3
import json
import os

def send_processing_messages():
    """Send document processing messages to SQS"""
    
    # Configure AWS client for LocalStack
    sqs_client = boto3.client(
        'sqs',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test'),
        region_name='us-east-1'
    )
    
    queue_name = 'document-processing-queue'
    
    # Create queue if it doesn't exist
    try:
        response = sqs_client.create_queue(QueueName=queue_name)
        queue_url = response['QueueUrl']
        print(f"✅ Queue ready: {queue_name}")
    except Exception as e:
        print(f"❌ Error with queue: {e}")
        return
    
    # Sample processing messages
    messages = [
        {
            "file_key": "doc1.txt",
            "bucket": "document-storage",
            "file_id": "doc_001",
            "metadata": {"category": "ai", "priority": "high"}
        },
        {
            "file_key": "doc2.txt",
            "bucket": "document-storage", 
            "file_id": "doc_002",
            "metadata": {"category": "ml", "priority": "medium"}
        },
        {
            "file_key": "doc3.txt",
            "bucket": "document-storage",
            "file_id": "doc_003", 
            "metadata": {"category": "nlp", "priority": "high"}
        },
        {
            "file_key": "doc4.txt",
            "bucket": "document-storage",
            "file_id": "doc_004",
            "metadata": {"category": "cv", "priority": "low"}
        },
        {
            "file_key": "doc5.txt",
            "bucket": "document-storage",
            "file_id": "doc_005",
            "metadata": {"category": "rl", "priority": "medium"}
        }
    ]
    
    # Send messages
    for msg in messages:
        try:
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(msg),
                MessageAttributes={
                    'file_id': {
                        'StringValue': msg['file_id'],
                        'DataType': 'String'
                    },
                    'category': {
                        'StringValue': msg['metadata']['category'],
                        'DataType': 'String'
                    }
                }
            )
            print(f"✅ Sent message for: {msg['file_key']}")
        except Exception as e:
            print(f"❌ Error sending message for {msg['file_key']}: {e}")
    
    print(f"\n🎉 Messages sent to SQS queue: {queue_name}")
    return queue_url

if __name__ == "__main__":
    print("📨 Sending processing messages to SQS...")
    send_processing_messages()
