# Tytopya 🚀

## 1. Overview
**Tytopya** is an advanced AI-powered platform designed for seamless information processing. It combines state-of-the-art **Text Summarization** (both Abstractive and Extractive) with a sophisticated **RAG (Retrieval-Augmented Generation) Chatbot**. Whether you need to condense large documents or hold an intelligent conversation about your private data, Tytopya provides a premium, glassmorphic user experience to get it done.

## 2. System Architecture
The platform is built on a modern distributed architecture:
- **Frontend**: A high-performance, responsive UI crafted with **Bootstrap 5**, **GSAP** for smooth animations, and **SweetAlert2** for elegant user feedback. The design follows a curated **Glassmorphism** aesthetic.
- **Backend**: A robust **Flask** application serving as the orchestration layer, handling authentication, data management, and API routes.
- **Asynchronous Processing**: Uses **Celery** with **Redis** as a message broker to handle heavy NLP and machine learning tasks without blocking the user interface.
- **AI Core**:
    - **Summarization**: Leverages **T5-Large** for abstractive summaries and **spaCy/NLTK** for extractive analysis.
    - **RAG Engine**: Powered by **LangChain** and **CTransformers**, utilizing **GGUF** quantized models for high-quality local inferencing.
- **Data Layer**:
    - **Relation Database**: **SQLite** for user profiles, session metadata, and chat/summary history.
    - **Vector Store**: **ChromaDB** for efficient document indexing and similarity search in the RAG pipeline.

## 3. File Architecture
```text
tytopya/
├── app.py               # Entry point for the Flask application
├── celery_worker.py    # Entry point for the Celery background worker
├── webapp/              # Main application package
│   ├── auth.py          # User authentication and registration logic
│   ├── routes.py        # Core dashboard, search, and history routes
│   ├── summarization.py # Text & PDF summarization pipelines (Celery-enabled)
│   ├── rag.py           # Retrieval-Augmented Generation & ChromaDB logic
│   ├── chatbot.py       # Intent-based supporting chatbot
│   ├── models.py        # SQLAlchemy database schemas
│   ├── static/          # Assets (CSS/JS/Images)
│   └── templates/       # Jinja2 HTML templates
├── instance/            # Local SQLite database storage
├── chroma_db/           # Persistent vector search indexes
├── uploads/             # User-uploaded documents (PDF, CSV, TXT)
├── Dockerfile           # Application container definition
└── docker-compose.yml   # Multi-service orchestration (Web, Worker, Redis)
```

## 4. Tools and Concepts
- **Glassmorphism UI**: A premium design language featuring translucent layers and vivid highlights.
- **Multi-Session RAG**: Support for independent chat sessions, each with its own set of documents and context memory.
- **Deep Search**: A case-insensitive search engine that queries both original data and AI-generated outputs.
- **AJAX Integration**: All heavy operations (deletion, submission) happen asynchronously for a "no-reload" experience.
- **Local AI**: Optimized to run powerful LLMs locally using GGUF quantization.

## 5. References & Resources
- 📊 [ChatBot Dataset (Kaggle)](https://www.kaggle.com/datasets/ahmedsamir6788/chatbot-json-data-set)
- 🧠 [Mistral-7B-Instruct-v0.2 (GGUF)](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF) - The primary model for RAG.
- 📝 [T5-Large (Summarization)](https://huggingface.co/google-t5/t5-large) - The model used for abstractive summarization.
- 📖 [Text-to-Text Transfer Transformer (T5) Paper](https://arxiv.org/abs/1910.10683) - Reference for the T5 architecture.

## 6. How to Install
> [!IMPORTANT]
> **Models Download**: Due to their size, the AI models are not included in the repository. You must download them manually:
> 1. Download `mistral-7b-instruct-v0.2.Q4_K_M.gguf` from the link above.
> 2. Create the folder `webapp/models/` if it doesn't exist.
> 3. Place the downloaded `.gguf` file inside `webapp/models/`.

### Prerequisites
- Python 3.11+
- Redis Server (if running locally)
- Docker & Docker Compose (Recommended)

### Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/ahmedsamir45/tytopya.git
   cd tytopya
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 7. How to Run
### Method A: Using Docker (Recommended)
This is the simplest way to run the entire stack (Web + Worker + Redis) automatically:
```bash
docker-compose up --build
```
Access the app at `http://localhost:5000`.

### Method B: Manual (Development)
1. Ensure Redis is running on `localhost:6379`.
2. Start the Celery worker (in a new terminal):
   ```bash
   celery -A celery_worker.celery_app worker --loglevel=info
   ```
3. Start the Flask application:
   ```bash
   python app.py
   ```

## 8. License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

