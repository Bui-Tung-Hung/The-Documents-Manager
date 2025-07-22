from pathlib import Path
import tempfile
import boto3
import uuid
from langchain_unstructured import UnstructuredLoader
from typing import Any, Callable, Optional, Dict
import config

class S3DocumentLoader:
    def __init__(
        self, 
        bucket: str, 
        key: str, 
        fileID: str,
        *,

        ## Optional parameters for S3 connection and document processing
        region_name: Optional[str] = config.region_name,
        aws_access_key_id: Optional[str] = config.aws_access_key_id,
        aws_secret_access_key: Optional[str] = config.aws_secret_access_key,
        endpoint_url: str = config.endpoint_url,

        ## Parameters for document loading and splitting
        chunking_strategy: Optional[str] = "by_title",
        strategy: Optional[str] = "auto",
        max_characters: Optional[int] = 1000,
        overlap: Optional[int] = 200,

        ## Optional function to add custom metadata to documents
        # The function should accept a dictionary and return a dictionary
        # This allows for flexible metadata handling, such as adding custom keys or values
        # If None, no additional metadata will be added
        add_to_metadata: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,

        preview_n: int = 3,
        ):


        """Initialize the S3DocumentLoader with bucket and key."""

        self.bucket = bucket
        self.key = key
        self.fileID = fileID
        self.uuid = str(uuid.uuid4())
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.chunking_strategy = chunking_strategy
        self.strategy = strategy
        self.max_characters = max_characters
        self.overlap = overlap
        self.preview_n = preview_n
        self.add_to_metadata = add_to_metadata
        self.s3 = boto3.client(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=endpoint_url,
        )
        self.docs = []

    def download(self, temp_dir: str):
        self.local_path = Path(temp_dir) / Path(self.key).name
        self.local_path.parent.mkdir(parents=True, exist_ok=True)
        self.s3.download_file(self.bucket, self.key, str(self.local_path))
        print(f"✅ Downloaded: s3://{self.bucket}/{self.key} → {self.local_path}")

    def load_and_split(self):
        loader = UnstructuredLoader(
            str(self.local_path),
            chunking_strategy=self.chunking_strategy,
            strategy=self.strategy,
            max_characters=self.max_characters, overlap=self.overlap, 
        )
        self.docs = loader.load()

        print(f"✅ Loaded {len(self.docs)} documents.")
        

    def clean_metadata(self):
        for doc in self.docs:
            doc.metadata = {
                "fileID": self.fileID,
                #"uuid": self.uuid,
                #"source": doc.metadata.get("source", f"s3://{self.bucket}/{self.key}"),
            }

            if self.add_to_metadata:
                custom_metadata = self.add_to_metadata(doc.metadata.copy())
                if custom_metadata and isinstance(custom_metadata, dict):
                    doc.metadata.update(custom_metadata)
                else:
                    print(f"⚠️ Warning: add_to_metadata did not return a dictionary or returned None for doc {doc.metadata.get('source')}.")

    def preview(self):
        print("\n\npreviewing first", self.preview_n, "documents:")
        for doc in self.docs[:self.preview_n]:
            print("\n\n", "-" * 80)
            print("📄 Metadata:", doc.metadata)
            print("📄 Content preview:", doc.page_content[:100], "...\n")


    def get(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.download(tmp)
            self.load_and_split()
            self.clean_metadata()
            #self.preview()
        return self.docs

# 👇 Sử dụng class
if __name__ == "__main__":
    loader = S3DocumentLoader(bucket="bibox-bucket", key="123456", fileID="test_file_id")
    docs = loader.get()
    for doc in docs:
        print("Document Metadata:", doc.metadata)
        print("Document Content:", doc.page_content[:100], "...")
        print("-" * 80)
        print()
