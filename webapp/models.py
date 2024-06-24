from datetime import datetime
from webapp import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Question(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    data = db.Column(db.String(10000))

    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Response(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Texts(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(30))
    data = db.Column(db.String(100000000))
    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    count = db.Column(db.Integer)


class Summaries(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(30))
    abs = db.Column(db.String(100000000))
    ext = db.Column(db.String(100000000))
    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Feedbacks(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    feedback = db.Column(db.String(10000))

    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))




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


    def __repr__(self):
        return f"User('{self.fname}', '{self.lname}', '{self.username}', '{self.email}')"