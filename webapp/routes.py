
from sqlalchemy import or_, func
from webapp.models import Question,Response,Texts,Summaries,Feedbacks,PDFChat
from flask import render_template ,request,jsonify,flash
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
    page_texts = request.args.get('page_texts', 1, type=int)
    page_chats = request.args.get('page_chats', 1, type=int)
    page_pdf = request.args.get('page_pdf', 1, type=int)
    
    per_page = 5
    
    texts_pagination = Texts.query.filter_by(user_id=current_user.id).order_by(Texts.date.desc()).paginate(page=page_texts, per_page=per_page, error_out=False)
    
    # Text chats (Question/Response pairs)
    chats_pagination = Question.query.filter_by(user_id=current_user.id).order_by(Question.date.desc()).paginate(page=page_chats, per_page=per_page, error_out=False)

    return render_template("dashboard.html", 
                           title="dashboard",
                           custom="dashboard",
                           js="dashboard",
                           user=current_user,
                           texts=texts_pagination,
                           chats=chats_pagination)

@routes1.route("/update_profile", methods=['POST'])
@login_required
def update_profile():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    
    if fname and lname:
        current_user.fname = fname
        current_user.lname = lname
        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating profile.", "error")
    else:
        flash("First and Last name cannot be empty.", "warning")
    
    from flask import redirect, url_for
    return redirect(url_for('routes1.dashboard'))



@routes1.route('/deletetext', methods=['POST'])
def delete_text():
    data = json.loads(request.data)
    textId = data['textId']
    text = Texts.query.get(textId)
   
    if text:
        if text.user_id == current_user.id:
            db.session.delete(text)
            db.session.commit()
            flash(f"The text was deleted succesfully", "success")
    return jsonify({})

@routes1.post('/deletemessage')
@routes1.get('/deletemessage')
def delete_message():  
    data = json.loads(request.data)
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


@routes1.route("/search", methods=["GET", "POST"])
def findSearch():
    query_text = (request.form.get("search") or request.args.get("search", "")).strip().lower()
    category = (request.form.get("category") or request.args.get("category", "all")).strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if current_user.is_authenticated and query_text:
        texts_results = []
        chats_results = []
        
        # Search in Summaries if category is 'all' or 'summaries'
        if category in ['all', 'summaries']:
            texts_query = Texts.query.join(Summaries, isouter=True).filter(
                Texts.user_id == current_user.id,
                or_(
                    func.lower(Texts.title).contains(query_text),
                    func.lower(Texts.data).contains(query_text),
                    func.lower(Summaries.abs).contains(query_text),
                    func.lower(Summaries.ext).contains(query_text)
                )
            ).distinct()
            texts_pagination = texts_query.paginate(page=page, per_page=per_page, error_out=False)
            texts_results = texts_pagination.items
        else:
            texts_pagination = None
        
        # Search in Chat History if category is 'all' or 'chats'
        if category in ['all', 'chats']:
            chats_query = Question.query.join(Response, isouter=True).filter(
                Question.user_id == current_user.id,
                or_(
                    func.lower(Question.data).contains(query_text),
                    func.lower(Response.data).contains(query_text)
                )
            ).distinct()
            chats_pagination = chats_query.paginate(page=page, per_page=per_page, error_out=False)
            chats_results = chats_pagination.items
        else:
            chats_pagination = None
        
        # Calculate total results
        total_results = len(texts_results) + len(chats_results)
        
        return render_template("result.html", 
                               custom="result", 
                               js="result", 
                               texts=texts_results,
                               chats=chats_results,
                               texts_pagination=texts_pagination,
                               chats_pagination=chats_pagination,
                               query=query_text,
                               category=category,
                               length=total_results)
    else:
        return render_template("result.html", custom="result", js="result", 
                             texts=[], chats=[], 
                             texts_pagination=None, chats_pagination=None,
                             query="", category="all", length=0)

