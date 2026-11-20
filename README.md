
🤖 AI-Powered Document Management & Multi-User RAG Chatbot

An enterprise-ready, production-oriented AI Document Management Admin Panel and Multi-User AI Chatbot powered by Retrieval-Augmented Generation (RAG), Hybrid Search (Dense + Sparse BM25), Enterprise Guardrails, and Automated Zero-Cost Web Search Fallback.

The system enables administrators to upload diverse document formats (PDF, DOCX, TXT, CSV, Excel), index them into a high-speed vector database, and manage role-based document permissions so authenticated users can query authorized documents with complete citation traceability.

🌟 Key Features
Multi-Format Document Ingestion: Supports parsing, cleaning, and indexing of .pdf, .docx, .txt, .csv, .xlsx, and .xls files.
Production-Grade RAG Pipeline:
Smart recursive text chunking (1,000-character windows with 200-character overlap).
Dense 384-dimensional vector embeddings using Hugging Face sentence-transformers/all-MiniLM-L6-v2.
Sub-millisecond vector similarity search using FAISS CPU (IndexFlatIP).
Hybrid Search (Dense + Sparse with RRF):
Combines Dense Semantic Search (FAISS embeddings) with Sparse Lexical Search (BM25Okapi).
Merges search ranks via Reciprocal Rank Fusion (RRF) to accurately retrieve both conceptual context and exact technical IDs/codes (e.g. invoice numbers, section tags).
Enterprise Security Guardrails:
Input Guardrails: Blocks prompt injection attacks, jailbreak patterns ("ignore previous instructions", "system override"), and malicious scripts. Automatically redacts Personally Identifiable Information (PII) like credit cards, SSNs, Aadhaar, and API keys.
Output Guardrails: Verifies factual grounding against retrieved context, detects potential hallucinations, and prevents internal prompt or secret leaks.
Automated Free Web Search Fallback:
If a user question cannot be answered from uploaded documents, the system automatically triggers a 100% free live web search (DuckDuckGo engine), synthesizes a cited answer, and tags the response as 🌐 Found via Web Search.
Granular Role-Based Access Control (RBAC):
Admin: Uploads, deletes, and reprocesses documents, manages user accounts, and assigns document permissions via an interactive UI modal.
User: Restricted strictly to authorized documents. Unauthorized document chunks are filtered at the backend level before vector search.
Modern ChatGPT-Style Dark Interface:
Responsive single-page application built with React.js, Tailwind CSS, and Lucide icons.
Multi-session chat drawer with automatic conversation titling, source citation badges, and chat deletion.
Zero-Cost Architecture: Operates with PostgreSQL, FAISS, Hugging Face models, and free search providers with zero mandatory paid API subscriptions.
🏗️ System Architecture
text
[ React.js + Tailwind Frontend ]
            │
            │ REST API / JWT over HTTP (Port 8000)
            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Gateway                  │
│                                                             │
│   [ Auth & RBAC Guard ] ──► [ Input Guardrails (PII/Attack) ]│
│                                           │                 │
│                                           ▼                 │
│                      ┌────────────────────────────────────┐ │
│                      │        Hybrid Retrieval Engine     │ │
│                      │  FAISS (Dense) + BM25 (Sparse RRF) │ │
│                      └─────────────────┬──────────────────┘ │
│                                        │                    │
│                                        ▼                    │
│                      [ Hugging Face LLM (Flan-T5/Qwen) ]     │
│                                        │                    │
│                              Answer in Documents?           │
│                                 /              \            │
│                       [YES]    /                \   [NO]    │
│                               ▼                  ▼          │
│                      [Output Guardrails]   [Free Web Search]│
│                               │                  │          │
│                               └────────┬─────────┘          │
│                                        │                    │
│                                        ▼                    │
│                          [ Final Cited Response ]           │
└────────────────────────────────────────┬────────────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
       [ PostgreSQL 18 Relational DB ]              [ Local FAISS Vector Store ]
     Users, Permissions, Chunks, Chats              384-Dim Normalized Embeddings
🗂️ Project Directory Structure
text
ai-doc-manager/
├── run_backend.bat                  # 1-Click launcher for FastAPI backend
├── run_frontend.bat                 # 1-Click launcher for Vite React frontend
├── README.md                        # Documentation & setup guide
│
├── backend/                         # FastAPI Python Backend
│   ├── main.py                      # Application entry point, DB init, routers & CORS
│   ├── config.py                    # Pydantic environment configuration (.env loader)
│   ├── database.py                  # SQLAlchemy engine & session factory
│   ├── requirements.txt             # Python package dependencies
│   ├── .env                         # Secrets vault (DB URL, HF Token, JWT Key)
│   │
│   ├── models/                      # SQLAlchemy Relational Models (PostgreSQL)
│   │   ├── user.py                  # User, UserGroup, GroupMember, UserRole
│   │   ├── document.py              # Document, DocumentPermission, DocumentChunk
│   │   ├── conversation.py          # Conversation, ChatMessage, ActivityLog
│   │   └── __init__.py
│   │
│   ├── schemas/                     # Pydantic Schemas (Request/Response Validation)
│   │   ├── auth.py                  # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── document.py              # DocumentResponse, AssignPermissionRequest
│   │   ├── chat.py                  # AskRequest, AskResponse, MessageResponse
│   │   └── __init__.py
│   │
│   ├── routers/                     # REST API Endpoints (Traffic Handlers)
│   │   ├── auth.py                  # /auth/login, /auth/register, /auth/me
│   │   ├── documents.py             # /documents/upload, /documents/, /documents/permissions
│   │   ├── chat.py                  # /chat/ask, /chat/conversations
│   │   ├── admin.py                 # /admin/stats, /admin/users, /admin/groups
│   │   └── __init__.py
│   │
│   ├── services/                    # Core Business Logic Layer
│   │   ├── auth_service.py          # Salted Bcrypt hashing & JWT token lifecycle
│   │   ├── document_service.py      # File validation, disk persistence & async pipeline
│   │   ├── rag_service.py           # Hybrid retrieval, guardrails & web fallback workflow
│   │   └── __init__.py
│   │
│   └── rag/                         # Core AI & Search Modules
│       ├── extractor.py             # Raw text extraction (PDF, DOCX, TXT, CSV, XLSX)
│       ├── chunker.py               # Recursive text chunking with context overlap
│       ├── embedder.py              # MiniLM 384-d vector embeddings generator
│       ├── vector_store.py          # FAISS index wrapper & metadata persistence
│       ├── hybrid_search.py         # BM25Okapi lexical search + Reciprocal Rank Fusion (RRF)
│       ├── guardrails.py            # Prompt injection defense, PII masking & grounding check
│       ├── llm.py                   # Hugging Face inference caller with local fallback
│       └── __init__.py
│
└── frontend/                        # React.js SPA (Vite)
    ├── index.html                   # HTML entry point with dark theme styles
    ├── package.json                 # Node dependencies & build scripts
    ├── vite.config.js               # Vite React bundler configuration
    ├── tailwind.config.js           # Tailwind CSS framework theme configuration
    ├── postcss.config.js            # PostCSS configuration
    │
    └── src/
        ├── main.jsx                 # React root renderer
        ├── App.jsx                  # React Router definitions & protected route guards
        ├── index.css                # Global Tailwind CSS directives & scrollbar styles
        │
        ├── api/
        │   └── client.js            # Central Axios HTTP client with JWT interceptor
        │
        ├── context/
        │   └── AuthContext.jsx      # Global user session & authentication state
        │
        ├── components/
        │   └── Sidebar.jsx          # Role-based collapsible navigation sidebar
        │
        └── pages/
            ├── Login.jsx            # User & Admin login page
            ├── Register.jsx         # New user registration page
            ├── admin/
            │   ├── Dashboard.jsx    # System metrics, recent documents & audit log
            │   ├── Documents.jsx    # Document management & dynamic user access modal
            │   ├── UploadDocuments.jsx # Drag-and-drop file uploader
            │   └── Users.jsx        # User activation & account management
            └── user/
                ├── Dashboard.jsx    # User home screen & accessible documents view
                └── Chatbot.jsx      # Multi-threaded ChatGPT-style Q&A interface
🛠️ Technology Stack
Layer	Component	Version / Library	Purpose
Frontend	Framework	React 19 + Vite 8.3	High-performance reactive UI
	Styling	Tailwind CSS 3.4	Modern responsive dark theme
	Icons	Lucide React	Clean, lightweight UI icons
	HTTP Client	Axios 1.21	API requests with automated JWT injection
Backend	API Engine	FastAPI 0.115	Asynchronous REST framework
	Server	Uvicorn 0.30	High-throughput ASGI web server
	Validation	Pydantic v2 + Pydantic-Settings	Strict request/response validation
	Security	Bcrypt 5.0 + Python-Jose	Cryptographic password hashing & JWT tokens
Database	Relational	PostgreSQL 18 + SQLAlchemy 2.0	ACID-compliant metadata & access control
	Vector Store	FAISS CPU 1.8.0	High-speed semantic similarity index
AI & NLP	Embeddings	sentence-transformers	all-MiniLM-L6-v2 (384-dimensional dense vectors)
	Language Model	Hugging Face Transformers	google/flan-t5-base (Local) / Qwen2.5 (Cloud)
	Lexical Search	BM25Okapi (Pure Python)	Exact keyword matching & Reciprocal Rank Fusion
	Web Fallback	ddgs (DuckDuckGo Search)	100% free live web search fallback
⚙️ Quick Start Installation Guide
Prerequisites
Python 3.10+ (Tested on Python 3.12)
Node.js 18+ (Tested on Node 22)
PostgreSQL 14+ (Service running on port 5432)
Step 1: Database Setup

Open psql or pgAdmin 4 and create the relational database:

sql
CREATE DATABASE ai_doc_manager;
Step 2: Backend Setup
Open a terminal and navigate to the backend folder:
powershell
cd D:\ai-doc-manager\backend
Create and activate a Python virtual environment:
powershell
python -m venv venv
.\venv\Scripts\activate          # Windows PowerShell
# source venv/bin/activate       # Mac / Linux
Install backend dependencies:
powershell
pip install -r requirements.txt
Verify your .env configuration file:
ini
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ai_doc_manager
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
HF_TOKEN=hf_your_free_huggingface_token
HF_MODEL=Qwen/Qwen2.5-7B-Instruct
MAX_FILE_SIZE=52428800
UPLOAD_DIR=uploads
VECTOR_DB_DIR=vector_db
Start the backend server:
powershell
uvicorn main:app --reload --port 8000
(Or double-click D:\ai-doc-manager\run_backend.bat)

NOTE

On the first startup, FastAPI automatically builds all database tables in PostgreSQL and seeds the default Admin account.

Step 3: Frontend Setup
Open a new terminal and navigate to the frontend folder:
powershell
cd D:\ai-doc-manager\frontend
Install npm packages:
powershell
npm install
Start the Vite development server:
powershell
npm run dev
(Or double-click D:\ai-doc-manager\run_frontend.bat)
Step 4: Access the Application
Portal	URL	Purpose
Web Application	http://localhost:5173	React User & Admin interface
Backend REST API	http://localhost:8000	FastAPI server root
Interactive API Docs	http://localhost:8000/docs	Swagger UI documentation & testing
Default Administrator Credentials:
Email: admin@example.com
Password: admin123
🔒 Role-Based Access Control (RBAC) Workflow
Admin Ingestion: Log in as admin@example.com, navigate to Upload, and add documents. Documents are automatically parsed, chunked, and stored in FAISS.
Assign Permissions: In the Documents panel, click the Access button next to any document to assign view/query permissions to specific registered users.
User Q&A: Users can register their own accounts (/register) and log in. In the AI Chatbot, users can only query information from documents explicitly assigned to them.
Guaranteed Isolation: If a user attempts to ask questions about unauthorized documents, the backend RBAC filter completely excludes those chunks before vector retrieval.
📡 REST API Reference Overview
Method	Endpoint	Access Role	Description
POST	/auth/login	Public	Authenticates credentials and returns JWT bearer token
POST	/auth/register	Public	Registers a new standard user account
GET	/auth/me	Authenticated	Retrieves current logged-in user details
POST	/documents/upload	Admin	Uploads document and initiates async RAG pipeline
GET	/documents/	Authenticated	Lists authorized documents for the current user
DELETE	/documents/{id}	Admin	Deletes document and its associated vector chunks
POST	/documents/permissions	Admin	Grants document query access to a user
GET	/documents/{id}/permissions	Admin	Lists all users who have access to a document
DELETE	/documents/permissions/{id}	Admin	Revokes document access for a user
POST	/chat/ask	Authenticated	Queries Hybrid RAG pipeline with auto web fallback
GET	/chat/conversations	Authenticated	Lists user's conversation threads
GET	/chat/conversations/{id}/messages	Authenticated	Retrieves all messages in a specific chat session
DELETE	/chat/conversations/{id}	Authenticated	Deletes a conversation session
GET	/admin/stats	Admin	Returns system counts (users, documents, chats)
GET	/admin/users	Admin	Lists all registered users
PUT	/admin/users/{id}/toggle	Admin	Activates or deactivates a user account
📄 License & Attribution

Developed with modular, maintainable, and readable architecture. Free for educational, enterprise, and commercial adaptation under the MIT License.
