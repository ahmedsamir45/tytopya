from flask import Flask, render_template, url_for, flash, redirect, config
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_admin import Admin





app = Flask(__name__)

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"
cros = CORS()

# admin1 = Admin(app)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '3235T90IKEGARJOPAKFFWJAVSOZDMKrgrest5234tfbhu8iklo09iuytr'
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///tytopya.db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    from .routes import routes1
    from .auth import auth1
    from .summarization import summarization1
    from .chatbot import chatbot1
    from .admin import adminnbp, MyAdminIndexView,MyModelView,UserModelView
    from .models import User,Question,Texts,Response,Summaries,Feedbacks

    bcrypt.init_app(app)
    cros.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    admin1 = Admin(app, index_view=MyAdminIndexView())
    # admin1.add_view(MyModelView(User,db.session))
    admin1.add_view(MyModelView(Question,db.session))
    admin1.add_view(MyModelView(Response,db.session))
    admin1.add_view(MyModelView(Texts,db.session))
    admin1.add_view(MyModelView(Summaries,db.session))
    admin1.add_view(MyModelView(Feedbacks,db.session))
    admin1.add_view(UserModelView(User,db.session))

    app.register_blueprint(adminnbp)
    app.register_blueprint(routes1)
    app.register_blueprint(auth1)
    app.register_blueprint(chatbot1)
    app.register_blueprint(summarization1)

    with app.app_context():
        db.create_all()

    return app
