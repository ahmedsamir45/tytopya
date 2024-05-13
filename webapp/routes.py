
from webapp.models import User,Question,Response,Texts,Summaries,Feedbacks
from flask import render_template ,url_for,flash ,redirect,request,jsonify
from webapp.forms import RegistrationForm , LoginForm
from webapp import bcrypt,db,app
from flask_login import login_user,current_user,logout_user,login_required
from flask import Blueprint


routes1= Blueprint("routes1",__name__)

# start login logout register
@routes1.post("/register")
@routes1.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes1.summary'))
    form = RegistrationForm()
    
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fname=form.fname.data,lname=form.lname.data,username=form.username.data,email=form.email.data,password=hash_password)
     
    
        db.session.add(user)
        db.session.commit()
        flash(f"Account created successfully for {form.username.data}", "success")
        return redirect(url_for("routes1.login"))
    return render_template("register.html", title="Register", form=form)


@routes1.get("/login")
@routes1.post("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes1.summary'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if (user and bcrypt.check_password_hash(user.password , form.password.data)):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            flash("You have been logged in!", "success")
            return redirect(next_page) if next_page else redirect(url_for("routes1.home"))
        else:
            flash("Login Unsuccessful. Please check credentials", "danger")
    return render_template("login.html", title="Login", form=form)




@routes1.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("routes1.home"))

# end login logout register













# chat bot code
import random
import json
import pickle
import numpy as np
import nltk

from nltk.stem import WordNetLemmatizer
from keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open("webapp/intents2.json").read())



# paterns
words = pickle.load(open('words.pkl', 'rb'))

# tags 
classes = pickle.load(open('classes.pkl', 'rb'))

model1 = load_model('chatbot_model.h5')

"""
The code initializes the WordNetLemmatizer from NLTK, loads the intents data from a JSON file,
and loads the preprocessed data from pickle files.
It loads the words and classes used for training the model and loads the pre-trained model.
"""

def clean_up_sentence(sentence):

    # Tokenize the sentence into individual words
    sentence_words = nltk.word_tokenize(sentence)

    # Lemmatize each word to its base form
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    # Clean up the sentence
    sentence_words = clean_up_sentence(sentence)

    # Create a bag of words representation
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1

    return np.array(bag)


def predict_class(sentence):
    # Convert the sentence into a bag of words
    bow = bag_of_words(sentence)

    # Predict the intent using the loaded model
    res = model1.predict(np.array([bow]))[0]

    ERROR_THRESHOLD = 0.25
    # Filter out predictions below the error threshold
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    # Sort the results by probability in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    return_list = []
    for r in results:
        # Get the corresponding intent and its probability
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

    return return_list


def get_response(intents_list, intents_json):
    # Get the predicted intent
    tag = intents_list[0]['intent']

    list_of_intents = intents_json['intents']

    for i in list_of_intents:
        
        if i['tag'] == tag:
            
            # Randomly choose a response from the matched intent
            result = random.choice(i['responses'])
            break

    return result


print("GO! Bot is running!")
# end chat bot code

# start abstractiv text summarization
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
model = T5ForConditionalGeneration.from_pretrained('t5-large')
tokenizer = T5Tokenizer.from_pretrained('t5-large')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# end abstractive text summarization

# start extractive text summarization

import spacy

from spacy.lang.en.stop_words import STOP_WORDS

from string import punctuation
stopwords = list(STOP_WORDS)
nlp = spacy.load('en_core_web_sm')


# end extractive text summarization









@routes1.route("/")
@routes1.route("/home")
def home():
    return render_template("home.html" , title = "home" ,custom="home",js="home")



@routes1.route("/summary")
def summary():

    return render_template("summary.html" , title = "summary" ,custom="summary",js="summary" )

@routes1.post('/predict')
def predict():

    text = request.form.get("mean_radius")
    # abstractive
    text = ''.join(text)
    preprocessed_text = text.strip().replace('\n','')
    
    t5_input_text =  "summarize: "+preprocessed_text
    tokenized_text = tokenizer.encode(t5_input_text,min_length=50,return_tensors='pt', max_length=1500).to(device)
    summary_ids = model.generate(tokenized_text, min_length=50, max_length=300)
    summary_abs = tokenizer.decode(summary_ids[0], skip_special_tokens=True)


    # extractive
    doc=nlp(text)
    tokens = [token.text for token in doc]
    from string import punctuation
    punctuation = punctuation + '\n' 
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    max_frequency = max(word_frequencies.values())


    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word]/max_frequency

    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]


    from heapq import nlargest
    select_length = int(len(sentence_tokens)*0.2)
    summary = nlargest(select_length, sentence_scores, key = sentence_scores.get)
    final_summary_ext = [word.text for word in summary]
    summary_ext = ' '.join(final_summary_ext)


    if current_user.is_authenticated:
        text = Texts(data=text, user_id=current_user.id)
        summary = Summaries(abs=summary_abs, ext=summary_ext, user_id=current_user.id)
        try:
            
            db.session.add(text)
            db.session.add(summary)
            db.session.commit()
        except Exception as e:
            # Handle the exception, e.g., log the error
            print(f"Error occurred: {e}")


    return render_template("summary.html" , title = "summary" ,custom="summary",js="summary", summary_abs= summary_abs,summary_ext=summary_ext )








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
    summaries=Summaries.query.filter_by(user_id=current_user.id).all()
    question=Question.query.filter_by(user_id=current_user.id).all()
    response=Response.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html" , title = "dashboard" ,custom="dashboard",js="dashboard",user=current_user,dataPackge_Sum=zip(texts,summaries),dataPackge_chat=zip(question,response))


@routes1.post('/predictChat',  endpoint='predictChat')
@routes1.get('/predictChat',  endpoint='predictChat')
def predictChat():
    text2=request.get_json().get("message")
    print("======================================")
    print(text2)
    print(type(text2))
    print("======================================")
    ints = predict_class(text2)
    response = get_response(ints, intents)
    if current_user.is_authenticated:
        question = Question(data=text2, user_id=current_user.id)
        res = Response( data=response, user_id=current_user.id)
        try:
          
            db.session.add(question)
            db.session.add(res)
            db.session.commit()
        except Exception as e:
            # Handle the exception, e.g., log the error
            print(f"Error occurred: {e}")
    message={"answer":response}
    return jsonify(message)