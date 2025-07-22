from qdrant_manager import SearchDocument
import config


if __name__ == "__main__":
    searcher = SearchDocument(
        collection_name="TestCollection5",
        embedding_model="bge-m3:latest",
        url=config.url,
        api_key=config.api_key,
    )
    searcher.init()  # Initialize the searcher
    query = "self-attention"
    results = searcher.search(query, k=5)

    print(f"Found {len(results)} documents for query: '{query}'")
    for doc in results:
        print()
        print("Document Metadata:", doc.metadata)
        print("Document Content:", doc.page_content[:100], "...")
        print("-" * 80)