# 🔍 The Documents Manager - AI-Powered Document Search System

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Hệ thống tìm kiếm tài liệu thông minh sử dụng AI với khả năng hiểu ngữ nghĩa, tích hợp FastAPI + Ollama + Qdrant Cloud trong một container Docker duy nhất.

## 📋 Mục Lục

- [🚀 Quick Start (5 phút)](#-quick-start-5-phút)
- [✅ Kiểm Tra Hệ Thống](#-kiểm-tra-hệ-thống)
- [📋 API Reference](#-api-reference)
- [🏗️ Kiến Trúc Hệ Thống](#️-kiến-trúc-hệ-thống)
- [🔧 Cấu Hình](#-cấu-hình)
- [🚨 Xử Lý Sự Cố](#-xử-lý-sự-cố)
- [🧪 Testing](#-testing)
- [💻 Development](#-development)
- [📈 Performance & Scaling](#-performance--scaling)
- [🗺️ Roadmap](#️-roadmap)
- [📄 License](#-license)

---

## 🚀 Quick Start (5 phút)

### Yêu Cầu Hệ Thống
- ✅ **Docker** installed và running
- ✅ **Minimum 4GB RAM** available (khuyến nghị 8GB)
- ✅ **Port 8001** free
- ✅ **Internet connection** (để kết nối Qdrant Cloud & download models)

### Build & Run

```bash
# Clone repository
git clone https://github.com/Bui-Tung-Hung/The-Documents-Manager.git
cd The-Documents-Manager

# Build Docker image (lần đầu: 5-10 phút do download Ollama models)
docker build -t document-search-api .

# Run container
docker run --name doc-api -p 8001:8001 document-search-api
```

### ⏱️ Thời Gian Build Dự Kiến
- **Lần đầu tiên**: 5-10 phút (download Ollama BGE-M3 model ~1.2GB)
- **Lần sau**: 1-2 phút (sử dụng Docker cache)

---

## ✅ Kiểm Tra Hệ Thống

### 1. Health Check
```bash
curl http://localhost:8001/health
```

**Kết quả mong đợi:**
```json
{
  "status": "healthy",
  "message": "Document Search API is running"
}
```

### 2. API Documentation
Mở trình duyệt và truy cập:
```
http://localhost:8001/docs
```

### 3. Test Search Basic
```bash
curl -X POST "http://localhost:8001/search-files" \
     -H "Content-Type: application/json" \
     -d '{"query": "attention mechanism"}'
```

### 4. Container Logs
Để xem logs container:
```bash
docker logs doc-api
```

**Logs thành công sẽ hiển thị:**
```
🚀 Starting Document Search API...
🔥 Starting Ollama service...
✅ Ollama should be ready now
✅ Qdrant connection successful
🌟 Starting FastAPI server on http://localhost:8001
INFO: Application startup complete.
```

---

## 📋 API Reference

### Base URL
```
http://localhost:8001
```

### Endpoints

#### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "message": "Document Search API is running"
}
```

#### 2. API Information
```http
GET /
```
**Response:**
```json
{
  "message": "Document Search API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "search": "/search-files",
    "docs": "/docs"
  }
}
```

#### 3. Document Search
```http
POST /search-files
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "your search query here"
}
```

**Response:**
```json
{
  "query": "attention mechanism",
  "results": [
    {
      "file_id": "doc_123",
      "score": 0.95,
      "content": "Attention mechanisms allow models to focus..."
    }
  ]
}
```

#### 4. Interactive Documentation
```http
GET /docs
```
Swagger UI với khả năng test API trực tiếp.

### cURL Examples

```bash
# Health check
curl http://localhost:8001/health

# Search documents
curl -X POST "http://localhost:8001/search-files" \
     -H "Content-Type: application/json" \
     -d '{"query": "transformer model"}'

# Get API info
curl http://localhost:8001/
```

---

## 🏗️ Kiến Trúc Hệ Thống

### Technology Stack
- **🌐 FastAPI**: Modern Python web framework
- **🤖 Ollama + BGE-M3**: Local embedding generation
- **🗄️ Qdrant Cloud**: Vector database
- **🐳 Docker**: Containerization
- **🔍 Langchain**: AI framework integration

### Data Flow
```
User Query → FastAPI → Ollama BGE-M3 → Vector Embedding → Qdrant Search → Ranked Results
```

### Component Architecture
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Ollama     │    │  Qdrant Cloud   │
│   (Port 8001)   │◄──►│   BGE-M3     │◄──►│   Vector DB     │
│   Web Interface │    │   Embeddings │    │   Search Engine │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

### Key Features
- ✅ **Semantic Search**: Hiểu ngữ nghĩa thay vì exact matching
- ✅ **Real-time Embeddings**: Generate embeddings on-demand
- ✅ **Scalable Vector DB**: Cloud-based Qdrant
- ✅ **RESTful API**: Chuẩn REST API với documentation
- ✅ **Health Monitoring**: Built-in health checks
- ✅ **CORS Support**: Ready for web integration

---

## 🔧 Cấu Hình

### Environment Variables

File `config_docker.py` chứa các cấu hình chính:

```python
# Qdrant Cloud Configuration
url = "https://your-qdrant-cloud-url"
api_key = "your-qdrant-api-key"

# Docker-specific settings
log_level = "INFO"
```

### Ollama Configuration
- **Model**: BGE-M3 (Multilingual embedding model)
- **Size**: ~1.2GB
- **Languages**: Hỗ trợ đa ngôn ngữ
- **Dimension**: 1024 vector dimensions

### Port Configuration
- **API Port**: 8001 (có thể thay đổi trong `start_api.sh`)
- **Ollama Port**: 11434 (internal)

### Memory Settings
- **Minimum RAM**: 4GB
- **Recommended RAM**: 8GB
- **Ollama Model**: ~1.2GB VRAM/RAM

---

## 🚨 Xử Lý Sự Cố

### Container Exits Immediately

**Triệu chứng:**
```bash
docker run document-search-api
# Container stops after a few seconds
```

**Nguyên nhân:** Ollama service chưa khởi động đúng cách

**Giải pháp:**
1. Kiểm tra logs:
```bash
docker logs <container-name>
```

2. Nếu thấy lỗi "Failed to connect to Ollama":
```bash
# Rebuild image
docker build --no-cache -t document-search-api .
```

### Out of Memory Error

**Triệu chứng:**
```
Error: cannot allocate memory
```

**Giải pháp:**
1. Tăng Docker memory limit (Settings → Resources → Memory)
2. Đóng các ứng dụng khác đang sử dụng RAM
3. Khuyến nghị: minimum 4GB available RAM

### Port Already in Use

**Triệu chứng:**
```
Error: bind: address already in use
```

**Giải pháp:**
```bash
# Kiểm tra process đang sử dụng port 8001
lsof -i :8001

# Kill process nếu cần
kill -9 <PID>

# Hoặc sử dụng port khác
docker run -p 8002:8001 document-search-api
```

### Qdrant Connection Failed

**Triệu chứng:**
```
❌ Qdrant connection failed: Failed to connect
```

**Giải pháp:**
1. Kiểm tra internet connection
2. Verify Qdrant Cloud credentials trong `config_docker.py`
3. Kiểm tra firewall settings

### Build Fails - Model Download

**Triệu chứng:**
```
Error downloading model bge-m3:latest
```

**Giải pháp:**
1. Kiểm tra internet connection
2. Retry build:
```bash
docker build --no-cache -t document-search-api .
```

---

## 🧪 Testing

### Sử dụng Test Script

```bash
# Chạy test script có sẵn
python test_api.py
```

**Kết quả mong đợi:**
```
🚀 Starting API tests...
🔍 Testing health endpoint...
Health Status: 200
🔍 Testing search endpoint...
Found 5 file_id results for 'attention mechanism'
```

### Manual Testing

```bash
# Test các endpoint chính
curl http://localhost:8001/health
curl http://localhost:8001/
curl -X POST "http://localhost:8001/search-files" -H "Content-Type: application/json" -d '{"query": "test"}'
```

### Load Testing

```bash
# Sử dụng curl để test concurrent requests
for i in {1..10}; do
  curl -X POST "http://localhost:8001/search-files" \
       -H "Content-Type: application/json" \
       -d '{"query": "test '$i'"}' &
done
wait
```

---

## 💻 Development

### Local Development Setup

```bash
# Clone và setup environment
git clone https://github.com/Bui-Tung-Hung/The-Documents-Manager.git
cd The-Documents-Manager

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_api.txt
```

### Code Structure

```
├── app.py                 # Main FastAPI application
├── models.py             # Pydantic models
├── search_service.py     # Search logic
├── qdrant_manager.py     # Qdrant integration
├── config_docker.py     # Configuration
├── start_api.sh         # Startup script
├── Dockerfile           # Container definition
├── requirements*.txt    # Python dependencies
└── test_api.py         # Test scripts
```

### Adding New Features

1. **New API Endpoint:**
   - Add endpoint trong `app.py`
   - Define models trong `models.py`
   - Add business logic trong appropriate service

2. **New Search Features:**
   - Modify `search_service.py`
   - Update `qdrant_manager.py` nếu cần

### Running Locally (không Docker)

```bash
# Cần Ollama running locally
ollama serve &
ollama pull bge-m3:latest

# Start API
uvicorn app:app --reload --port 8001
```

---

## 📈 Performance & Scaling

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 5GB
- Network: Stable internet

**Recommended:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 10GB SSD
- Network: High-speed internet

### Performance Characteristics

- **Cold start**: 10-15 seconds (model loading)
- **Search latency**: 200-500ms per query
- **Throughput**: 10-50 requests/second (depending on hardware)
- **Concurrent users**: 5-20 simultaneous

### Scaling Considerations

**Horizontal Scaling:**
- Run multiple containers with load balancer
- Share Qdrant Cloud instance
- Use container orchestration (k8s, Docker Swarm)

**Vertical Scaling:**
- Increase container memory limits
- Use faster CPUs
- Optimize Ollama model settings

**Production Optimizations:**
- Use production ASGI server (Gunicorn + Uvicorn)
- Implement caching layer
- Add monitoring và logging
- Use CDN for static assets

---

## 🗺️ Roadmap

### ✅ Current Features (v1.0)
- [x] Document search với semantic understanding
- [x] RESTful API với FastAPI
- [x] Docker containerization
- [x] Health monitoring
- [x] Interactive API documentation
- [x] BGE-M3 multilingual embeddings

### 🚧 In Progress (v1.1)
- [ ] Batch document upload
- [ ] File format support (PDF, DOCX, TXT)
- [ ] Search result ranking improvements
- [ ] Performance optimizations

### 📋 Planned Features (v2.0)
- [ ] **Web UI Interface**: React-based frontend
- [ ] **Multi-model Support**: Additional embedding models
- [ ] **Advanced Search**: Filters, date ranges, file types
- [ ] **User Management**: Authentication & authorization
- [ ] **Analytics Dashboard**: Search metrics & insights

### 🔮 Future Vision (v3.0+)
- [ ] **Chat Interface**: RAG-based document Q&A
- [ ] **Multi-language UI**: Vietnamese, English, others
- [ ] **Enterprise Features**: SSO, audit logs, compliance
- [ ] **AI Insights**: Document classification, summarization
- [ ] **Mobile App**: iOS/Android applications

---

## 📄 License

MIT License - xem file [LICENSE](LICENSE) để biết chi tiết.

### Credits & Acknowledgments

**Core Technologies:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Ollama](https://ollama.ai/) - Local LLM & embedding server
- [Qdrant](https://qdrant.tech/) - Vector database
- [BGE-M3](https://huggingface.co/BAAI/bge-m3) - Multilingual embedding model

**Development:**
- Developed by [Bui-Tung-Hung](https://github.com/Bui-Tung-Hung)
- Community contributions welcome!

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Support

- 📧 **Issues**: [GitHub Issues](https://github.com/Bui-Tung-Hung/The-Documents-Manager/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Bui-Tung-Hung/The-Documents-Manager/discussions)
- 📖 **Documentation**: [Wiki](https://github.com/Bui-Tung-Hung/The-Documents-Manager/wiki)

---

<div align="center">

**⭐ Nếu project này hữu ích, hãy cho một star! ⭐**

Made with ❤️ by [Bui-Tung-Hung](https://github.com/Bui-Tung-Hung)

</div>