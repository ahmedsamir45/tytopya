from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import current_user, login_required
from pypdf import PdfReader
import os
import shutil
from webapp import db
from webapp.models import PDFChat, ChatSession, SessionDocument, ChatMessage
from celery import shared_task
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import CTransformers
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
import time
import pandas as pd
import datetime

rag = Blueprint('rag', __name__)

# Paths
CHROMA_DB_DIR = os.path.join(os.getcwd(), "chroma_db")
MODEL_PATH = "webapp/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# Initialize persistence if not exists
if not os.path.exists(CHROMA_DB_DIR):
    os.makedirs(CHROMA_DB_DIR)

@shared_task(bind=True)
def process_document_task(self, file_path, session_id):
    """Celery task to process document (PDF, CSV, TXT) and store in session-specific vector store."""
    try:
        filename = os.path.basename(file_path)
        file_ext = filename.split('.')[-1].lower()
        
        loader_text = ""
        if file_ext == 'pdf':
            pdf_reader = PdfReader(file_path)
            for page in pdf_reader.pages:
                loader_text += page.extract_text() + "\n"
        elif file_ext == 'csv':
            df = pd.read_csv(file_path)
            loader_text = df.to_string()
        elif file_ext in ['txt', 'md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                loader_text = f.read()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_text(loader_text)
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Unique persistent directory for each session
        persist_directory = os.path.join(CHROMA_DB_DIR, f"session_{session_id}")
        
        # We append to the session's vector store if it already exists
        # This allows multiple files per session
        vector_db = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            persist_directory=persist_directory,
            metadatas=[{"filename": filename, "chunk": i} for i in range(len(chunks))]
        )
        
        from webapp import db
        from webapp.models import SessionDocument, ChatSession
        
        # Register in SessionDocument table
        new_doc = SessionDocument(
            session_id=session_id,
            filename=filename,
            file_type=file_ext,
            file_path=file_path, # Keep for record, but we delete temp file below
            chunk_count=len(chunks)
        )
        db.session.add(new_doc)
        
        # Update session title if it's still default
        session = ChatSession.query.get(session_id)
        if session and session.title == "New Chat":
            session.title = filename[:50]
            
        db.session.commit()
        
        # Keep the file in a permanent storage or delete if only relying on vector store
        # For now, let's keep it in a session subfolder or remove it
        # os.remove(file_path) 
        return {'status': 'success', 'message': f'Processed {filename} ({len(chunks)} chunks).'}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {'status': 'error', 'message': str(e)}

@rag.route('/chat-doc')
@login_required
def chat_doc():
    return render_template('rag.html', title="Chat with Document", custom="rag")

@rag.route('/chat-doc/sessions', methods=['GET'])
@login_required
def get_sessions():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.updated_at.desc()).all()
    return jsonify([{
        'id': s.id,
        'title': s.title,
        'updated_at': s.updated_at.isoformat()
    } for s in sessions])

@rag.route('/chat-doc/session/create', methods=['POST'])
@login_required
def create_session():
    new_session = ChatSession(user_id=current_user.id)
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'id': new_session.id, 'title': new_session.title})

@rag.route('/chat-doc/session/<int:session_id>', methods=['GET'])
@login_required
def get_session_details(session_id):
    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    messages = [{
        'role': m.role,
        'content': m.content,
        'timestamp': m.timestamp.isoformat()
    } for m in session.messages]
    
    docs = [{
        'filename': d.filename,
        'type': d.file_type
    } for d in session.documents]
    
    return jsonify({
        'id': session.id,
        'title': session.title,
        'messages': messages,
        'documents': docs
    })

@rag.route('/chat-doc/session/<int:session_id>/title', methods=['PUT'])
@login_required
def update_session_title(session_id):
    data = request.get_json()
    new_title = data.get('title')
    if not new_title:
        return jsonify({'error': 'Title is required'}), 400
        
    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    session.title = new_title
    db.session.commit()
    return jsonify({'success': True, 'title': session.title})

@rag.route('/chat-doc/session/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    session = ChatSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Also delete ChromaDB collection directory
    persist_directory = os.path.join(CHROMA_DB_DIR, f"session_{session_id}")
    if os.path.exists(persist_directory):
        try:
            shutil.rmtree(persist_directory)
        except Exception as e:
            print(f"Error deleting session directory: {e}")
            
    db.session.delete(session)
    db.session.commit()
    return jsonify({'success': True})

@rag.route('/chat-doc/upload', methods=['POST'])
@login_required
def upload_doc():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    session_id = request.form.get('session_id')
    
    if file.filename == '' or not session_id:
        return jsonify({'error': 'Invalid request'}), 400

    session = ChatSession.query.get(session_id)
    if not session or session.user_id != current_user.id:
        return jsonify({'error': 'Invalid session'}), 403

    # Save to upload folder
    upload_dir = os.path.join(os.getcwd(), "uploads", f"session_{session_id}")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)

    # Trigger Task
    task = process_document_task.delay(file_path, session_id)
    return jsonify({'success': True, 'task_id': task.id, 'message': 'Processing document...'})

@rag.route('/chat-doc/status/<task_id>')
@login_required
def get_task_status(task_id):
    from celery.result import AsyncResult
    celery_app = current_app.extensions['celery']
    task_result = AsyncResult(task_id, app=celery_app)
    
    result_data = {
        'status': task_result.status,
        'task_id': task_id,
        'task_result': None
    }
    
    if task_result.ready():
        res = task_result.result
        if isinstance(res, dict):
            result_data['task_result'] = res
            if res.get('status') == 'error':
                result_data['status'] = 'FAILURE'
        else:
            result_data['task_result'] = {'status': 'success', 'data': str(res)}
            
    return jsonify(result_data)

@rag.route('/chat-doc/ask', methods=['POST'])
@login_required
def ask():
    data = request.get_json()
    question = data.get('question')
    session_id = data.get('session_id')
    
    if not question or not session_id:
        return jsonify({'error': 'Invalid request'}), 400

    session = ChatSession.query.get(session_id)
    if not session or session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    persist_directory = os.path.join(CHROMA_DB_DIR, f"session_{session_id}")
    if not os.path.exists(persist_directory):
        return jsonify({'error': 'Please upload documents to this session first.'}), 400

    try:
        # Load embeddings and DB
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        
        llm = CTransformers(
            model=MODEL_PATH,
            model_type="mistral",
            config={
                'max_new_tokens': 512, 
                'temperature': 0.7,
                'context_length': 2048
            }
        )
        
        # Get history for context (last 5 messages)
        history_objs = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        history_objs.reverse()
        
        history_str = ""
        for msg in history_objs:
            history_str += f"{msg.role}: {msg.content}\n"
            
        # Simplified QA with History
        retriever = vector_db.as_retriever(search_kwargs={"k": 3})
        
        # Use PromptTemplate instead of raw string to satisfy validation
        template = f"Previous conversation:\n{history_str}\n\nContext based on documents:\n{{context}}\n\nUser Question: {question}\n\nAssistant:" if history_str else \
                   f"Context based on documents:\n{{context}}\n\nUser Question: {question}\n\nAssistant:"
        
        prompt_obj = PromptTemplate(template=template, input_variables=["context"])

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_obj}
        )
        
        # Note: Langchain 0.1+ uses invoke, but here we seem to be using older version or custom wrapper
        # based on previous code. If qa_chain({"query": question}) worked before:
        response = qa_chain({"query": question})
        answer = response['result']
        
        # Save messages to database
        user_msg = ChatMessage(session_id=session_id, role='user', content=question)
        assistant_msg = ChatMessage(session_id=session_id, role='assistant', content=answer)
        db.session.add(user_msg)
        db.session.add(assistant_msg)
        
        # Update session updated_at
        session.updated_at = datetime.datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'answer': answer,
            'session_id': session_id
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@rag.route('/chat-doc/delete-legacy', methods=['POST'])
@login_required
def delete_pdf_chat_legacy():
    """Delete old PDFChat records (pre-session migration)"""
    try:
        data = request.get_json(force=True)
        chat_id = data.get('chatId')
        if not chat_id:
             return jsonify({'error': 'No chat ID provided'}), 400
             
        chat = PDFChat.query.get(chat_id)
        if chat and chat.user_id == current_user.id:
            db.session.delete(chat)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'error': 'Unauthorized or not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
