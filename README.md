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
- 📄 [Our Research Paper](https://drive.google.com/file/d/1ITdAK8VfUG73gKDb3NsjtkKbkFqShuMP/view)
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
- Redis server
- 8GB+ RAM (for running Mistral-7B on CPU)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ahmedsamir45/tytopya.git
cd tytopya
```

2. **Create virtual environment**
```bash
python -m venv TYpackges
# Windows
TYpackges\Scripts\activate
# Linux/Mac
source TYpackges/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download the Mistral-7B model**
```bash
# Download from HuggingFace
# Place in: webapp/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

5. **Set up the database**
```bash
python
>>> from webapp import db, create_app
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

6. **Start Redis** (in a separate terminal)
```bash
redis-server
```

7. **Start Celery worker** (in a separate terminal)
```bash
# Windows
run_worker.bat
# Linux/Mac
celery -A celery_worker.celery_app worker --loglevel=info
```

8. **Run the application**
```bash
python app.py
```

9. **Open your browser**
```
http://localhost:5000
```

## 📚 Documentation

- [Backend Libraries](LIBRARIES.md) - Detailed explanation of AI/ML libraries
- [Frontend Libraries](FRONTEND_LIBRARIES.md) - UI framework documentation
- [API Documentation](docs/API.md) - REST API endpoints (coming soon)

## 🛠️ Configuration

Key configuration in `config.py`:
- `SECRET_KEY` - Flask session encryption
- `SQLALCHEMY_DATABASE_URI` - Database connection
- `CELERY_BROKER_URL` - Redis connection for Celery

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://python.langchain.com/) - RAG framework
- [Mistral AI](https://mistral.ai/) - Mistral-7B model
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [HuggingFace](https://huggingface.co/) - Model hosting and transformers

## 📧 Contact

Ahmed Samir - ahmedsamer6788@gmail.com

Project Link: [https://github.com/ahmedsamir45/tytopya](https://github.com/ahmedsamir45/tytopya)

## ⚠️ Known Issues

- RAG responses are slow on CPU (30-60s) - GPU support coming soon
- Windows requires `--pool=solo` for Celery worker
- ChromaDB requires SQLite 3.35.0+

## 🗺️ Roadmap

- [ ] Implement streaming responses (SSE) for faster perceived performance
- [ ] Add GPU support for Mistral-7B
- [ ] Docker containerization
- [ ] API authentication with JWT
- [ ] Multi-language support
- [ ] Export chat history to PDF
