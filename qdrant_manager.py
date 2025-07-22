# qdrant_manager.py
from __future__ import annotations

from typing import Optional, List
import uuid
import config_docker as config

from langchain_qdrant import QdrantVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance


from loader import S3DocumentLoader

class QdrantModule:
    """Base class: khởi tạo và load/tao collection rỗng."""

    def __init__(
        self,
        collection_name: str = "DocumentsControl3",
        embedding_model: str = "bge-m3:latest",
        url: str = config.url,
        api_key: str = config.api_key,
    ):
        self.collection_name = collection_name
        self.url = url
        self.api_key = api_key
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.qdrant: Optional[QdrantVectorStore] = None

    # ---------- internal helpers ----------
    def _collection_exists(self) -> bool:
        client = QdrantClient(url=self.url, api_key=self.api_key)
        try:
            client.get_collection(collection_name=self.collection_name)
            return True
        except Exception:
            return False

    def _create_empty_collection(self) -> None:
        """Tạo collection mới (trống) với dimension của embedding."""
        client = QdrantClient(url=self.url, api_key=self.api_key)
        dim = len(self.embeddings.embed_query("init"))
        client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        print(f"🆕 Created empty collection: **{self.collection_name}**")

    # ---------- public ----------
    def init(self) -> QdrantVectorStore:
        """Load nếu có, nếu không thì tạo mới rỗng, rồi trả về vectorstore."""
        if not self._collection_exists():
            self._create_empty_collection()
        else:
            print(f"✅ Loaded existing collection: **{self.collection_name}**")

        self.qdrant = QdrantVectorStore.from_existing_collection(
            embedding=self.embeddings,
            url=self.url,
            api_key=self.api_key,
            prefer_grpc=False,
            collection_name=self.collection_name,
        )
        return self.qdrant

    def get_vectorstore(self) -> QdrantVectorStore:
        if self.qdrant is None:
            raise RuntimeError("Vectorstore chưa init – hãy gọi init() trước.")
        return self.qdrant


class QdrantManager(QdrantModule):
    """Quản lý thao tác cao hơn: thêm document, …"""

    def __init__(
        self,
        collection_name: str = "DocumentsControl3",
        embedding_model: str = "bge-m3:latest",
        url: str = config.url,
        api_key: str = config.api_key,
    ):
        # ⚠️ Truyền đúng thứ tự tham số của lớp cha
        super().__init__(collection_name, embedding_model, url, api_key)

    # --------- high‑level ops ----------
    def add_documents(self, docs) -> None:
        """Thêm documents vào collection."""
        if not self.qdrant:
            raise RuntimeError("Vectorstore chưa init – hãy gọi init() trước.")
        if not docs:
            print("⚠️ Không có documents để thêm.")
            return

        # Chuyển đổi sang Document nếu cần
        if isinstance(docs, list) and all(isinstance(doc, str) for doc in docs):
            docs = [Document(page_content=doc) for doc in docs]

        self.qdrant.add_documents(docs)
        print(f"✅ Đã thêm {len(docs)} documents vào collection: **{self.collection_name}**")




class SearchDocument(QdrantManager):
    """Tìm kiếm tài liệu trong Qdrant dựa trên fileID."""

    def __init__(
        self,
        collection_name: str = "DocumentsControl3",
        embedding_model: str = "bge-m3:latest",
        url: str = config.url,
        api_key: str = config.api_key,
    ):
        super().__init__(collection_name, embedding_model, url, api_key)

    def search(self, query: str, k: int = 5) -> List[Document]:
        """Tìm kiếm tài liệu dựa trên câu truy vấn."""
        if not self.qdrant:
            raise RuntimeError("Vectorstore chưa init – hãy gọi init() trước.")
        results = self.qdrant.similarity_search(query, k=k)
        return results

    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """Tìm kiếm tài liệu với scores."""
        if not self.qdrant:
            raise RuntimeError("Vectorstore chưa init – hãy gọi init() trước.")
        results = self.qdrant.similarity_search_with_score(query, k=k)
        return results
    

