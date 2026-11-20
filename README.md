# 🤖 AI-Powered Document Management & Multi-User RAG Chatbot

<p align="center">
  <strong>An AI-powered document management platform with secure, multi-user Retrieval-Augmented Generation (RAG).</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react" />
  <img src="https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql" />
  <img src="https://img.shields.io/badge/AI-RAG-purple" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

## 📌 Overview

**AI-Powered Document Management & Multi-User RAG Chatbot** is an intelligent document management platform that allows administrators to upload, organize, and manage documents while providing authenticated users with an AI-powered question-answering interface.

The system combines **Retrieval-Augmented Generation (RAG), Hybrid Search, FAISS Vector Database, BM25, Hugging Face LLMs, and Enterprise Security Guardrails** to generate context-aware responses from uploaded documents.

It also includes an automated DuckDuckGo web search fallback when relevant information cannot be found in the uploaded documents.

### 🎯 Main Objectives

- Build an intelligent document management system.
- Implement a complete RAG pipeline.
- Support multiple document formats.
- Provide secure multi-user document access.
- Improve retrieval accuracy using Hybrid Search.
- Protect the application using input and output guardrails.
- Generate answers with source-based citations.
- Provide automatic web search fallback.

---

## 🌟 Key Features

### 1. Multi-Format Document Ingestion

Supports uploading and processing multiple document formats:

- PDF (`.pdf`)
- Word (`.docx`)
- Text (`.txt`)
- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)

Uploaded documents are extracted, cleaned, chunked, embedded, and indexed for semantic retrieval.

### 2. Advanced RAG Pipeline

The system uses a complete Retrieval-Augmented Generation workflow.

- Recursive text splitting.
- Chunk size: 1,000 characters.
- Chunk overlap: 200 characters.
- Hugging Face embeddings.
- Model: `sentence-transformers/all-MiniLM-L6-v2`.
- 384-dimensional vector embeddings.
- FAISS CPU vector database.
- Context-aware answer generation.

### 3. Hybrid Search (Dense + Sparse)

Combines two retrieval techniques to improve search quality.

**Dense Search**
- Uses semantic embeddings.
- Powered by FAISS.
- Finds conceptually related information.

**Sparse Search**
- Uses BM25Okapi.
- Finds exact keywords, identifiers, and technical terms.

**Reciprocal Rank Fusion (RRF)**

Combines the rankings from dense and sparse retrieval to produce a unified result.

### 4. Enterprise Security Guardrails

**Input Guardrails**
- Detects prompt injection patterns.
- Blocks common jailbreak attempts.
- Detects malicious input patterns.
- Masks sensitive information such as Aadhaar numbers, credit card numbers, and API keys.

**Output Guardrails**
- Checks responses against retrieved context.
- Detects potentially unsupported answers.
- Helps prevent hallucinations.
- Protects internal prompts and sensitive information.

### 5. Automated Free Web Search Fallback

When the uploaded documents do not contain sufficient information:

1. The RAG pipeline evaluates the retrieved context.
2. If relevant information is unavailable, web search is triggered.
3. DuckDuckGo retrieves relevant information.
4. The LLM generates a response using the search results.
5. The response is identified with a `🌐 Found via Web Search` label.

### 6. Role-Based Access Control (RBAC)

The application supports two primary roles.

| Feature | Admin | User |
|---|:---:|:---:|
| Upload documents | ✅ | ❌ |
| Delete documents | ✅ | ❌ |
| Manage users | ✅ | ❌ |
| Assign document permissions | ✅ | ❌ |
| View authorized documents | ✅ | ✅ |
| Ask questions | ✅ | ✅ |
| Access restricted documents | ❌ | ❌ |

Document permissions are enforced on the backend before retrieval.

### 7. Modern ChatGPT-Style Interface

- React-based single-page application.
- Responsive dark interface.
- Multi-session conversations.
- Automatic conversation titles.
- Source citation badges.
- Chat history management.
- JWT-based authentication.
- Role-based navigation.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[React + Tailwind Frontend] -->|REST API / JWT| B[FastAPI Backend]

    B --> C[Authentication & RBAC]
    C --> D[Input Guardrails]
    D --> E[Document Permission Filter]

    E --> F[Hybrid Retrieval Engine]

    F --> G[FAISS Dense Search]
    F --> H[BM25 Sparse Search]

    G --> I[Reciprocal Rank Fusion]
    H --> I

    I --> J[Hugging Face LLM]

    J --> K{Sufficient Document Context?}

    K -->|Yes| L[Output Guardrails]
    K -->|No| M[DuckDuckGo Web Search]

    M --> N[Web-Based Answer Generation]

    N --> L
    L --> O[Final Cited Response]

    B --> P[(PostgreSQL Database)]
    F --> Q[(FAISS Vector Store)]
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 19 | User interface |
| Build Tool | Vite | Frontend development |
| Styling | Tailwind CSS | Responsive UI |
| Icons | Lucide React | Interface icons |
| HTTP Client | Axios | API communication |
| Backend | FastAPI | REST API |
| Server | Uvicorn | ASGI server |
| Validation | Pydantic | Request validation |
| Authentication | JWT | Secure authentication |
| Password Security | Bcrypt | Password hashing |
| Database | PostgreSQL 18 | Relational data storage |
| ORM | SQLAlchemy 2.0 | Database operations |
| Vector Database | FAISS CPU | Semantic retrieval |
| Embeddings | Sentence Transformers | Text embeddings |
| Embedding Model | all-MiniLM-L6-v2 | 384-dimensional embeddings |
| LLM | Hugging Face | Answer generation |
| Search | BM25Okapi | Keyword retrieval |
| Rank Fusion | RRF | Hybrid retrieval |
| Web Search | DuckDuckGo (ddgs) | External search fallback |

---

## 📂 Project Directory Structure

```text
ai-doc-manager/
│
├── run_backend.bat
├── run_frontend.bat
├── README.md
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── requirements.txt
│   ├── .env
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── conversation.py
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── document.py
│   │   ├── chat.py
│   │   └── __init__.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── chat.py
│   │   ├── admin.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── document_service.py
│   │   ├── rag_service.py
│   │   └── __init__.py
│   │
│   └── rag/
│       ├── extractor.py
│       ├── chunker.py
│       ├── embedder.py
│       ├── vector_store.py
│       ├── hybrid_search.py
│       ├── guardrails.py
│       ├── llm.py
│       └── __init__.py
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    │
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css
        │
        ├── api/
        │   └── client.js
        │
        ├── context/
        │   └── AuthContext.jsx
        │
        ├── components/
        │   └── Sidebar.jsx
        │
        └── pages/
            ├── Login.jsx
            ├── Register.jsx
            │
            ├── admin/
            │   ├── Dashboard.jsx
            │   ├── Documents.jsx
            │   ├── UploadDocuments.jsx
            │   └── Users.jsx
            │
            └── user/
                ├── Dashboard.jsx
                └── Chatbot.jsx
```

---

## ⚙️ Installation & Setup

### Prerequisites

Make sure you have installed:

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Git
- Hugging Face account and API token

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-doc-manager.git

cd ai-doc-manager
```

### Step 2: Create PostgreSQL Database

Open pgAdmin or PostgreSQL terminal.

```sql
CREATE DATABASE ai_doc_manager;
```

### Step 3: Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file inside the backend directory.

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ai_doc_manager

SECRET_KEY=your-super-secret-key

ACCESS_TOKEN_EXPIRE_MINUTES=60

HF_TOKEN=hf_your_huggingface_token

HF_MODEL=Qwen/Qwen2.5-7B-Instruct

MAX_FILE_SIZE=52428800

UPLOAD_DIR=uploads

VECTOR_DB_DIR=vector_db
```

**Important:** Replace the database password, Hugging Face token, and secret key with your own values.

Never upload your `.env` file or API tokens to GitHub.

### Step 5: Start Backend Server

```bash
uvicorn main:app --reload --port 8000
```

Backend URL:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

### Step 6: Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## 🌐 Application URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Swagger API Docs | http://localhost:8000/docs |

---

## 🔐 Role-Based Access Control Workflow

### Admin Workflow

1. Log in using an administrator account.
2. Navigate to the document management dashboard.
3. Upload PDF, DOCX, TXT, CSV, or Excel documents.
4. Documents are extracted and processed through the RAG pipeline.
5. Assign document permissions to registered users.
6. Manage users and monitor system activity.

### User Workflow

1. Register a new account.
2. Log in using valid credentials.
3. View documents assigned by the administrator.
4. Open the AI chatbot.
5. Ask questions about authorized documents.
6. Receive AI-generated responses with source references.

### Document Security

The backend applies user-specific document permissions before vector retrieval.

This ensures that users cannot retrieve information from documents they are not authorized to access.

---

## 📡 REST API Reference

### Authentication APIs

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/login` | Public | User login |
| POST | `/auth/register` | Public | User registration |
| GET | `/auth/me` | Authenticated | Current user information |

### Document APIs

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/documents/upload` | Admin | Upload document |
| GET | `/documents/` | Authenticated | List authorized documents |
| DELETE | `/documents/{id}` | Admin | Delete document |
| POST | `/documents/permissions` | Admin | Assign document permissions |
| GET | `/documents/{id}/permissions` | Admin | View document permissions |
| DELETE | `/documents/permissions/{id}` | Admin | Revoke document permissions |

### Chat APIs

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/chat/ask` | Authenticated | Ask AI chatbot |
| GET | `/chat/conversations` | Authenticated | List conversations |
| GET | `/chat/conversations/{id}/messages` | Authenticated | Retrieve chat messages |
| DELETE | `/chat/conversations/{id}` | Authenticated | Delete conversation |

### Admin APIs

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/admin/stats` | Admin | System statistics |
| GET | `/admin/users` | Admin | List registered users |
| PUT | `/admin/users/{id}/toggle` | Admin | Activate/deactivate user |

---

## 🧠 How the RAG Pipeline Works

The application follows these processing stages:

**1. Document Upload**

The administrator uploads documents through the frontend.

**2. Text Extraction**

The backend extracts text from the uploaded documents using format-specific extraction logic.

**3. Text Chunking**

Extracted content is divided into smaller chunks using recursive text splitting.

**4. Embedding Generation**

Each chunk is converted into a 384-dimensional vector using the Hugging Face embedding model.

**5. Vector Storage**

The generated embeddings and associated metadata are stored in FAISS.

**6. Hybrid Retrieval**

When a user asks a question:

- Dense retrieval searches semantic similarity.
- Sparse retrieval searches keyword relevance.
- RRF combines both rankings.

**7. LLM Generation**

The retrieved context is passed to the Hugging Face language model to generate an answer.

**8. Guardrail Validation**

The generated response is checked against the available context.

**9. Web Search Fallback**

If sufficient document information is unavailable, DuckDuckGo search is used as an alternative information source.

**10. Final Response**

The chatbot returns the generated answer along with relevant source information.

---

## 🔒 Security Considerations

- Keep API tokens and database credentials in environment variables.
- Never commit `.env` files.
- Use strong JWT signing secrets.
- Change default administrator credentials before deployment.
- Enforce document permissions on the backend.
- Validate uploaded file types and sizes.
- Apply appropriate input and output validation.
- Use HTTPS when deploying publicly.

---

## 🚀 Future Enhancements

Potential improvements for future development:

- Docker-based deployment.
- Cloud-based document storage.
- Advanced reranking models.
- Document-level audit analytics.
- More embedding model options.
- Background document processing.
- Automated testing and CI/CD.
- Enhanced monitoring and logging.

---

## 👨‍💻 Author

**Shreyas Kapadiya**

AI / Machine Learning / Generative AI Enthusiast

- GitHub: [Your GitHub Profile](https://github.com/YOUR_USERNAME)
- LinkedIn: [Your LinkedIn Profile](https://www.linkedin.com/in/YOUR_USERNAME/)

---

## 📄 License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.

---

<p align="center">
  ⭐ If you find this project interesting, consider giving it a star!
</p>
