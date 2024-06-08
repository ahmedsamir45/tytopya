
from webapp.models import Question,Response,Texts,Summaries,Feedbacks
from flask import render_template ,request,jsonify
from webapp import db
from flask_login import current_user,login_required
from flask import Blueprint
import json

routes1= Blueprint("routes1",__name__)






@routes1.route("/")
@routes1.route("/home")
def home():
    return render_template("home.html" , title = "home" ,custom="home",js="home")









@routes1.post("/about")
@routes1.get("/about")
def about():
    if request.method=="POST":
        feed= request.form.get("feadback")
        if current_user.is_authenticated:
            feedback = Feedbacks(feedback=feed,user_id=current_user.id )
        else:
            feedback = Feedbacks(feedback=feed,user_id="no one")

        db.session.add(feedback)
        db.session.commit()
    return render_template("about.html" , title = "about" ,custom="about",js="about")

@login_required
@routes1.route("/dashboard")
def dashboard():
    texts=Texts.query.filter_by(user_id=current_user.id).all()
    count = len(Texts.query.filter_by(user_id=current_user.id).all())
    summaries=Summaries.query.filter_by(user_id=current_user.id).all()
    question=Question.query.filter_by(user_id=current_user.id).all()
    response=Response.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html" , title = "dashboard" ,custom="dashboard",js="dashboard",user=current_user,dataPackge_Sum=zip(texts,summaries),count=count,dataPackge_chat=zip(question,response))


@routes1.post('/deletetext')
def delete_note():  
    data = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    textId = data['textId']
    text = Texts.query.get(textId)
    if text:
        if text.user_id == current_user.id:
            db.session.delete(text)
            db.session.commit()
    return jsonify({})