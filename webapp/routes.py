
from webapp.models import Question,Response,Texts,Summaries,Feedbacks
from flask import render_template ,request,jsonify,flash
from webapp import db
from flask_login import current_user,login_required
from flask import Blueprint
import json

routes1= Blueprint("routes1",__name__)






@routes1.route("/")
@routes1.route("/home")
def home():
    flash(f"click collabse buttons in about and dashboard pages", "info")
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
    count_chat = len(Question.query.filter_by(user_id=current_user.id).all())
    summaries=Summaries.query.filter_by(user_id=current_user.id).all()
    question=Question.query.filter_by(user_id=current_user.id).all()
    response=Response.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html" , title = "dashboard" ,custom="dashboard",js="dashboard",user=current_user,dataPackge_Sum=zip(texts,summaries),count=count,count_chat=count_chat,dataPackge_chat=zip(question,response))




@routes1.route('/deletetext', methods=['POST'])
def delete_text():
    data = json.loads(request.data)  # this function expects a JSON from the INDEX.js file 
    textId = data['textId']
    text = Texts.query.get(textId)
   
    if text:
        if text.user_id == current_user.id:
            # Delete associated summary if it exists
            summary = Summaries.query.filter_by(id=text.id).first()
            if summary:
                db.session.delete(summary)
            
            db.session.delete(text)
            db.session.commit()
            flash(f"The text was deleted succesfully", "success")
    return jsonify({})

@routes1.post('/deletemessage')
@routes1.get('/deletemessage')
def delete_message():  
    data = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    mId = data['mId']
    message = Question.query.get(mId)
    if message:
        if message.user_id == current_user.id:
            response = Response.query.filter_by(id=message.id).first()
            if response:
                db.session.delete(response)
            db.session.delete(message)
            db.session.commit()
            flash(f"The message was deleted succesfully", "success")
    return jsonify({})


@routes1.get("/search")
@routes1.post("/search")
def findSearch():
    title = request.form.get("search")
    text_search = Texts.query.filter(Texts.title.ilike("%" + title + "%")).order_by(Texts.title).all()
    summary_search = Summaries.query.filter(Summaries.title.ilike("%" + title + "%")).order_by(Summaries.title).all()
    dataPackge_Sum= zip(text_search,summary_search)
    return render_template("result.html",custom="result",js="result",dataPackge_Sum = zip(text_search,summary_search),length=len(list(dataPackge_Sum)))

