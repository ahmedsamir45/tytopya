import datetime
from webapp import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Question(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime,nullable=False,default=datetime.datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    responses = db.relationship('Response', backref='question', lazy=True, cascade="all, delete-orphan")


class Response(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime,nullable=False,default=datetime.datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))


class Texts(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(30))
    data = db.Column(db.String(100000000))
    date = db.Column(db.DateTime,nullable=False,default=datetime.datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    count = db.Column(db.Integer)
    type = db.Column(db.String(10), default='text')
    summaries = db.relationship('Summaries', backref='text_source', lazy=True, cascade="all, delete-orphan")


class Summaries(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(30))
    abs = db.Column(db.String(100000000))
    ext = db.Column(db.String(100000000))
    date = db.Column(db.DateTime,nullable=False,default=datetime.datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text_id = db.Column(db.Integer, db.ForeignKey('texts.id'))

class Feedbacks(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    feedback = db.Column(db.String(10000))

    date = db.Column(db.DateTime,nullable=False,default=datetime.datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))




class PDFChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(10000))
    answer = db.Column(db.String(10000))
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# New models for multi-session RAG
class ChatSession(db.Model):
    """Represents a chat session/conversation with documents"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), default="New Chat")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    documents = db.relationship('SessionDocument', backref='session', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"ChatSession('{self.title}', user_id={self.user_id})"

class SessionDocument(db.Model):
    """Represents a document uploaded to a chat session"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10))  # pdf, csv, txt
    file_path = db.Column(db.String(500))
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    chunk_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f"SessionDocument('{self.filename}', type={self.file_type})"

class ChatMessage(db.Model):
    """Represents a message in a chat session"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"ChatMessage(role='{self.role}', session_id={self.session_id})"

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(125), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    question = db.relationship('Question',backref="author")
    response = db.relationship('Response',backref="author")
    texts = db.relationship('Texts',backref="author")
    summaries = db.relationship('Summaries',backref="author")
    feedbacks = db.relationship('Feedbacks',backref="author")
    pdf_chats = db.relationship('PDFChat', backref="author", lazy=True)
    chat_sessions = db.relationship('ChatSession', backref="author", lazy=True, cascade="all, delete-orphan")


    def __repr__(self):
        return f"User('{self.fname}', '{self.lname}', '{self.username}', '{self.email}')"