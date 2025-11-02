# FinWise-AI 🤖💰

**Multimodal RAG-Enhanced AI Assistant for Financial Document Analysis**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.108+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

FinWise-AI is an enterprise-grade, end-to-end AI system that analyzes financial documents using cutting-edge Generative AI, traditional ML, and MLOps practices. It combines:

- **🔍 RAG (Retrieval-Augmented Generation)** for accurate document querying
- **🤖 LLM Agents** for multi-step task orchestration
- **👁️ Multimodal AI** for processing text, images, and charts
- **📊 Traditional ML** for classification, forecasting, and clustering
- **🚀 Full MLOps Pipeline** with monitoring, CI/CD, and deployment

### Key Features

- ✅ Upload and analyze financial PDFs (bank statements, invoices, reports)
- ✅ Natural language querying (e.g., "What's the total expenses in Q3?")
- ✅ Automated expense categorization and trend forecasting
- ✅ Code generation for data visualization
- ✅ PII detection and redaction for compliance
- ✅ Multi-LLM support (OpenAI, Claude, Gemini)
- ✅ Production-ready with Docker, Kubernetes, and monitoring

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend UI   │ (Streamlit/Gradio)
└────────┬────────┘
         │
┌────────▼────────────────────────────────────┐
│         FastAPI Backend                     │
│  ┌──────────────────────────────────────┐  │
│  │  Document Processing Pipeline        │  │
│  │  (PDF/OCR → Text Extraction)         │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  RAG System                          │  │
│  │  (Vector DB + LLM Retrieval)         │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  LLM Agents (LangGraph)              │  │
│  │  - Financial Analysis Agent          │  │
│  │  - Code Generator Agent              │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │  ML Models                           │  │
│  │  (Classification/Forecasting)        │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         │
┌────────▼────────────────────────────────────┐
│  MLOps Infrastructure                       │
│  - MLflow (Tracking)                        │
│  - Prometheus (Monitoring)                  │
│  - Vector DB (Chroma/Weaviate)              │
│  - PostgreSQL (Metadata)                    │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- API Keys: OpenAI, Anthropic (Claude), or Google (Gemini)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/FinWise-AI.git
cd FinWise-AI
```

2. **Set up virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Initialize project structure**
```bash
python scripts/setup_project.py
```

6. **Run the application**
```bash
# Start backend
python main.py

# In another terminal, start frontend
streamlit run frontend/streamlit_app.py
```

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/api/docs
# Frontend: http://localhost:8501
```

## 📁 Project Structure

```
FinWise-AI/
├── src/
│   ├── api/              # FastAPI routes and schemas
│   ├── core/             # Configuration and security
│   ├── services/         # Business logic services
│   │   ├── document_processor.py
│   │   ├── rag_service.py
│   │   ├── llm_service.py
│   │   ├── agent_service.py
│   │   └── ml_service.py
│   ├── models/           # ML models and embeddings
│   ├── agents/           # LangGraph agents
│   └── utils/            # Utilities and helpers
├── data/                 # Data storage
│   ├── raw/
│   ├── processed/
│   └── embeddings/
├── models/               # Saved ML models
├── mlops/                # MLOps configurations
│   ├── airflow/          # Airflow DAGs
│   ├── monitoring/       # Prometheus/Grafana
│   └── mlflow/           # MLflow projects
├── deployment/           # Deployment configs
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
├── frontend/             # UI applications
├── tests/                # Unit and integration tests
├── notebooks/            # Jupyter notebooks
├── scripts/              # Utility scripts
├── docs/                 # Documentation
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following:

```env
# Application
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
DEBUG=true

# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Vector Database
VECTOR_DB_TYPE=chroma  # chroma, weaviate, or pinecone
CHROMA_PERSIST_DIR=./data/chroma

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/finwise

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8501"]
```

## 📊 Usage Examples

### 1. Upload and Analyze Documents

```python
import requests

# Upload a financial document
with open("bank_statement.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        files={"file": f}
    )
    doc_id = response.json()["document_id"]
```

### 2. Query Documents

```python
# Ask questions about your documents
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "What's the total expenses in Q3?",
        "document_ids": [doc_id]
    }
)
print(response.json()["answer"])
```

### 3. Generate Analysis Code

```python
# Generate Python code for visualization
response = requests.post(
    "http://localhost:8000/api/v1/generate-code",
    json={
        "task": "Create a bar chart of monthly expenses",
        "document_id": doc_id
    }
)
print(response.json()["code"])
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_rag.py -v
```

## 🚢 Deployment

### Kubernetes

```bash
# Apply Kubernetes configurations
kubectl apply -f deployment/kubernetes/

# Check deployment status
kubectl get pods
kubectl get services
```

### AWS SageMaker

```bash
# Deploy using Terraform
cd deployment/terraform
terraform init
terraform plan
terraform apply
```

## 📈 Monitoring

- **MLflow UI**: http://localhost:5000 (Experiment tracking)
- **Prometheus**: http://localhost:9090 (Metrics)
- **Grafana**: http://localhost:3000 (Dashboards)
- **API Docs**: http://localhost:8000/api/docs

## 🛠️ Tech Stack

### Core Technologies
- **Backend**: FastAPI, Python 3.10+
- **LLMs**: OpenAI GPT-4, Claude 3, Gemini
- **Frameworks**: LangChain, LangGraph, LlamaIndex
- **Vector DBs**: ChromaDB, Weaviate, Pinecone
- **ML**: Scikit-learn, PyTorch, Transformers

### MLOps
- **Tracking**: MLflow, Weights & Biases
- **Orchestration**: Apache Airflow, Kubeflow
- **Monitoring**: Prometheus, Grafana, ELK Stack
- **Versioning**: DVC, Git

### Deployment
- **Containers**: Docker, Kubernetes
- **Cloud**: AWS (SageMaker, Bedrock), GCP (Vertex AI)
- **IaC**: Terraform, Ansible
- **CI/CD**: GitHub Actions

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LangChain and LlamaIndex communities
- OpenAI, Anthropic, and Google for LLM APIs
- All open-source contributors

## 📧 Contact

**Your Name** - [@yourhandle](https://twitter.com/yourhandle)

Project Link: [https://github.com/yourusername/FinWise-AI](https://github.com/yourusername/FinWise-AI)

---

⭐ If you find this project useful, please consider giving it a star!
