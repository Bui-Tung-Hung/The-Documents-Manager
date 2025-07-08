from langchain_community.document_loaders import S3FileLoader



print("Loading documents from S3...")

loader = S3FileLoader(bucket="bibox-bucket", 
                        key="123456", 
                        aws_access_key_id="test", 
                        aws_secret_access_key="test", 
                        endpoint_url="http://localhost:4566"
)

documents = loader.load()


print(f"Loaded {len(documents)} documents from S3.")


# Print the first document's content
print("First document content:", documents[0].page_content[:100])  # Print first 100 characters