# main.py
from fastapi import FastAPI, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
import json
import boto3
import asyncio # Để chạy các tác vụ bất đồng bộ (ví dụ: SQS send)

# Import các lớp từ project của bạn
from qdrant_manager import SearchDocument
from loader import S3DocumentLoader
import config

# Khởi tạo FastAPI app
app = FastAPI(
    title="Document Management AI API",
    description="API for searching, chatting with documents, and automatic document classification.",
    version="1.0.0"
)

# --- Khởi tạo các đối tượng toàn cục (hoặc theo yêu cầu) ---
# Qdrant Searcher
# Khởi tạo một instance SearchDocument để tái sử dụng
try:
    qdrant_searcher = SearchDocument(
        collection_name="TestCollection6", # Đảm bảo tên collection khớp với upsert_to_vectorDB.py
        embedding_model="bge-m3:latest",
        url=config.url,
        api_key=config.api_key,
    )
    qdrant_searcher.init() # Khởi tạo kết nối Qdrant khi ứng dụng khởi động
    print("✅ Qdrant searcher initialized successfully.")
except Exception as e:
    print(f"❌ Failed to initialize Qdrant searcher: {e}")
    # Trong môi trường production, bạn có thể muốn dừng ứng dụng hoặc log lỗi nghiêm trọng hơn

# SQS client (nếu bạn muốn API kích hoạt upsert qua SQS)
# Tuy nhiên, thông thường việc upload file và trigger SQS nên là 2 bước riêng biệt
# Hoặc API sẽ trực tiếp gọi loader và manager nếu bạn muốn xử lý đồng bộ
try:
    sqs_client = boto3.client(
        'sqs',
        region_name=config.region_name,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        endpoint_url=config.endpoint_url
    )
    # Lấy URL của queue, hoặc tạo nếu chưa có (chỉ cho dev/LocalStack)
    try:
        response = sqs_client.get_queue_url(QueueName=config.queue_name)
        sqs_queue_url = response['QueueUrl']
    except sqs_client.exceptions.QueueDoesNotExist:
        response = sqs_client.create_queue(QueueName=config.queue_name)
        sqs_queue_url = response['QueueUrl']
    print(f"✅ SQS client initialized, queue URL: {sqs_queue_url}")
except Exception as e:
    print(f"❌ Failed to initialize SQS client: {e}")
    sqs_client = None # Đảm bảo biến này được đặt nếu có lỗi
    sqs_queue_url = None


# S3 client (nếu bạn muốn API tự upload file)
try:
    s3_client = boto3.client(
        's3',
        region_name=config.region_name,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        endpoint_url=config.endpoint_url
    )
    # Kiểm tra và tạo bucket nếu chưa có (chỉ cho dev/LocalStack)
    try:
        s3_client.head_bucket(Bucket=config.bucket)
    except s3_client.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404: # Bucket does not exist
            s3_client.create_bucket(Bucket=config.bucket)
            print(f"✅ S3 bucket '{config.bucket}' created.")
        else:
            raise e # Lỗi khác thì re-raise
    print(f"✅ S3 client initialized for bucket: {config.bucket}")
except Exception as e:
    print(f"❌ Failed to initialize S3 client: {e}")
    s3_client = None


# --- Định nghĩa các Model Pydantic cho Request/Response ---

class SearchRequest(BaseModel):
    query: str
    k: int = 5 # Số lượng tài liệu trả về mặc định

class DocumentResponse(BaseModel):
    page_content: str
    metadata: dict

class SearchResponse(BaseModel):
    query: str
    results: List[DocumentResponse]

class ChatRequest(BaseModel):
    query: str
    file_id: Optional[str] = None # Nếu muốn chat với tài liệu cụ thể
    chat_history: Optional[List[dict]] = [] # Lịch sử chat (nếu có)

class ChatResponse(BaseModel):
    answer: str
    source_documents: List[DocumentResponse] # Các tài liệu được sử dụng để tạo câu trả lời

class UploadFileResponse(BaseModel):
    message: str
    file_id: str
    s3_key: str


# --- Các Endpoint API ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to Document Management AI API!"}

# 1. API Tìm kiếm tài liệu
@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Tìm kiếm các tài liệu liên quan trong vector database dựa trên một câu truy vấn.
    """
    if qdrant_searcher.qdrant is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Qdrant service not initialized.")
    try:
        results = qdrant_searcher.search(request.query, k=request.k)
        # Chuyển đổi các đối tượng Document của Langchain sang DocumentResponse Pydantic
        response_results = [
            DocumentResponse(page_content=doc.page_content, metadata=doc.metadata)
            for doc in results
        ]
        return SearchResponse(query=request.query, results=response_results)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search failed: {e}")

# 2. API Chat với tài liệu (RAG - Retrieval Augmented Generation)
# Để làm chức năng này, bạn cần thêm một LLM (ví dụ: Ollama Llama2/Mistral)
# và một Chain/Agent từ Langchain.

# # Import LLM và chain từ Langchain
# from langchain_ollama import Ollama
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains.retrieval import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain

# # Khởi tạo LLM (nếu cần)
# try:
#     ollama_llm = Ollama(model="llama2") # Hoặc "mistral", "gemma"
#     print("✅ Ollama LLM initialized successfully.")
# except Exception as e:
#     print(f"❌ Failed to initialize Ollama LLM: {e}")
#     ollama_llm = None


# @app.post("/chat", response_model=ChatResponse)
# async def chat_with_documents(request: ChatRequest):
#     """
#     Chat với các tài liệu đã được lập chỉ mục bằng cách sử dụng Retrieval-Augmented Generation (RAG).
#     """
#     if ollama_llm is None:
#         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM not initialized.")
#     if qdrant_searcher.qdrant is None:
#         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Qdrant service not initialized.")

#     try:
#         # Bước 1: Tìm kiếm tài liệu liên quan
#         # Nếu có file_id, bạn có thể thêm bộ lọc vào tìm kiếm
#         # Ví dụ: results = qdrant_searcher.search(request.query, k=5, filter={"fileID": request.file_id})
#         # Hiện tại, QdrantManager của bạn chưa hỗ trợ filter, cần thêm vào.
#         # Tạm thời cứ search toàn bộ
#         retriever = qdrant_searcher.get_vectorstore().as_retriever(search_kwargs={"k": 5})

#         # Bước 2: Tạo Prompt Template
#         # Thêm chat_history vào prompt nếu bạn muốn duy trì ngữ cảnh cuộc trò chuyện
#         # Với Ollama, đảm bảo mô hình hỗ trợ chat_history
#         prompt_template = ChatPromptTemplate.from_messages([
#             ("system", "Bạn là một trợ lý AI hữu ích. Vui lòng trả lời câu hỏi dựa trên ngữ cảnh được cung cấp. Nếu bạn không biết câu trả lời, hãy nói rằng bạn không biết."),
#             # Nếu có chat_history, có thể thêm vào đây
#             # ("human", "{chat_history}\nQuestion: {input}"),
#             ("human", "{input}"),
#             ("assistant", "Dựa trên các thông tin sau:\n{context}\n\nTrả lời câu hỏi:"),
#         ])


#         # Bước 3: Tạo Retrieval Chain
#         question_answer_chain = create_stuff_documents_chain(ollama_llm, prompt_template)
#         rag_chain = create_retrieval_chain(retriever, question_answer_chain)

#         # Bước 4: Gọi Chain để lấy câu trả lời
#         response = rag_chain.invoke({"input": request.query, "chat_history": request.chat_history})

#         # Trích xuất nguồn tài liệu
#         source_docs = []
#         if "context" in response:
#             for doc in response["context"]:
#                 source_docs.append(DocumentResponse(page_content=doc.page_content, metadata=doc.metadata))

#         return ChatResponse(answer=response["answer"], source_documents=source_docs)

#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Chat failed: {e}")


# # 3. API Tự động phân loại tài liệu
# # Chức năng này phức tạp hơn và thường yêu cầu một mô hình ML/AI riêng
# # (ví dụ: một mô hình phân loại văn bản được huấn luyện)
# # hoặc sử dụng LLM để phân loại (ít chính xác hơn cho các tác vụ phân loại cụ thể).

# # Ví dụ đơn giản sử dụng LLM để "phân loại"
# class ClassifyRequest(BaseModel):
#     text_content: str
#     categories: List[str] # Ví dụ: ["Hợp đồng", "Báo cáo", "Hóa đơn"]

# class ClassifyResponse(BaseModel):
#     text_content: str
#     predicted_category: str
#     confidence: Optional[float] = None # Nếu mô hình hỗ trợ

# @app.post("/classify", response_model=ClassifyResponse)
# async def classify_document(request: ClassifyRequest):
#     """
#     Phân loại nội dung văn bản dựa trên các danh mục được cung cấp.
#     (Ví dụ đơn giản sử dụng LLM. Để chính xác, cần mô hình phân loại chuyên biệt.)
#     """
#     if ollama_llm is None:
#         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM not initialized.")

#     try:
#         # Prompt LLM để phân loại
#         prompt = f"""
#         Nội dung văn bản sau đây thuộc loại nào trong số các danh mục sau: {', '.join(request.categories)}?
#         Chỉ trả lời bằng tên danh mục duy nhất, không thêm bất kỳ văn bản nào khác.
#         Nếu bạn không chắc chắn, hãy trả lời 'Khác'.

#         Nội dung:
#         {request.text_content[:2000]} # Giới hạn độ dài để tránh lỗi token

#         Danh mục được dự đoán:
#         """
#         response = ollama_llm.invoke(prompt)
#         predicted_category = response.strip()

#         # Kiểm tra xem danh mục dự đoán có hợp lệ không
#         if predicted_category not in request.categories and predicted_category != "Khác":
#             # Nếu LLM trả về thứ gì đó không mong muốn, hãy đặt là "Khác"
#             predicted_category = "Khác"

#         return ClassifyResponse(text_content=request.text_content[:100] + "...", predicted_category=predicted_category)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Classification failed: {e}")


# # 4. API Upload tài liệu (trực tiếp qua API)
# # Tùy chọn: API này sẽ cho phép client upload file trực tiếp
# # thay vì dùng script `upload_to_s3.py`.
# # Sau khi upload lên S3, nó sẽ gửi tin nhắn SQS để kích hoạt quá trình upsert vào VectorDB.

# @app.post("/upload_document", response_model=UploadFileResponse)
# async def upload_document(file: UploadFile = File(...), file_id: str = None):
#     """
#     Upload một tài liệu lên S3 và kích hoạt quá trình xử lý (embedding và upsert vào VectorDB)
#     thông qua SQS.
#     """
#     if s3_client is None:
#         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="S3 client not initialized.")
#     if sqs_client is None or sqs_queue_url is None:
#         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="SQS client not initialized.")

#     if not file_id:
#         file_id = os.urandom(8).hex() # Tạo file_id ngẫu nhiên nếu không được cung cấp

#     s3_key = f"{file_id}/{file.filename}" # Cấu trúc key: file_id/original_filename

#     # Lưu file tạm thời và upload lên S3
#     with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
#         try:
#             content = await file.read() # Đọc nội dung file
#             tmp_file.write(content)
#             tmp_file_path = tmp_file.name
#         finally:
#             tmp_file.close() # Đảm bảo file được đóng

#     try:
#         s3_client.upload_file(tmp_file_path, config.bucket, s3_key)
#         print(f"Uploaded {file.filename} to s3://{config.bucket}/{s3_key}")

#         # Gửi tin nhắn SQS để kích hoạt xử lý
#         message_body = json.dumps({"S3_KEY": s3_key, "file_id": file_id})
#         sqs_client.send_message(
#             QueueUrl=sqs_queue_url,
#             MessageBody=message_body,
#         )
#         print(f"SQS message sent for file_id: {file_id}, S3_KEY: {s3_key}")

#         return UploadFileResponse(
#             message="File uploaded and processing triggered.",
#             file_id=file_id,
#             s3_key=s3_key
#         )
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload or trigger processing: {e}")
#     finally:
#         # Xóa file tạm thời
#         if os.path.exists(tmp_file_path):
#             os.remove(tmp_file_path)


# # Để chạy ứng dụng này, hãy sử dụng lệnh:
# # uvicorn main:app --reload --host 0.0.0.0 --port 8000
# # Sau đó truy cập http://127.0.0.1:8000/docs để xem tài liệu API tương tác.