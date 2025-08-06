#!/usr/bin/env python3
"""
Example script for uploading documents to S3 (LocalStack simulation)
"""

import boto3
import os
from pathlib import Path

def upload_sample_documents():
    """Upload sample documents to S3"""
    
    # Configure AWS client for LocalStack
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test'),
        region_name='us-east-1'
    )
    
    bucket_name = 'document-storage'
    
    # Create bucket if it doesn't exist
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"✅ Created bucket: {bucket_name}")
    except s3_client.exceptions.BucketAlreadyExists:
        print(f"✅ Bucket already exists: {bucket_name}")
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return
    
    # Sample documents
    documents = [
        {
            "key": "doc1.txt",
            "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models."
        },
        {
            "key": "doc2.txt", 
            "content": "Deep learning uses neural networks with multiple layers to model complex patterns in data."
        },
        {
            "key": "doc3.txt",
            "content": "Natural language processing enables computers to understand and process human language."
        },
        {
            "key": "doc4.txt",
            "content": "Computer vision allows machines to interpret and understand visual information from the world."
        },
        {
            "key": "doc5.txt",
            "content": "Reinforcement learning teaches agents to make decisions through interaction with environments."
        }
    ]
    
    # Upload documents
    for doc in documents:
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=doc["key"],
                Body=doc["content"].encode('utf-8'),
                ContentType='text/plain'
            )
            print(f"✅ Uploaded: {doc['key']}")
        except Exception as e:
            print(f"❌ Error uploading {doc['key']}: {e}")
    
    print(f"\n🎉 Sample documents uploaded to S3 bucket: {bucket_name}")
    return bucket_name, [doc["key"] for doc in documents]

if __name__ == "__main__":
    print("📤 Uploading sample documents to S3...")
    upload_sample_documents()
