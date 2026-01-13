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


def get_response(ints, intents_json):
    if not ints or not isinstance(ints[0], dict) or 'intent' not in ints[0]:
        return "Sorry, I didn't understand that. Could you please rephrase?"

    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            return random.choice(i['responses'])
    return "Sorry, I couldn't find an appropriate response."




from webapp.models import Question,Response
from flask import request,jsonify

from webapp import db
from flask_login import current_user
from flask import Blueprint




chatbot1= Blueprint("chatbot1",__name__)

@chatbot1.post('/predictChat',  endpoint='predictChat')
@chatbot1.get('/predictChat',  endpoint='predictChat')
def predictChat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"answer": "Error: No message received"}), 400
        
    text2 = data.get("message")
    print(f"Chat Message: {text2}")
    
    ints = predict_class(text2)
    response = get_response(ints, intents)
    
    if current_user.is_authenticated:
        try:
            question = Question(data=text2, user_id=current_user.id)
            db.session.add(question)
            db.session.commit()
            
            # Check if column exists before trying to save it
            # This is a temporary measure until DB migration is successful
            resp_args = {"data": response, "user_id": current_user.id}
            try:
                # Try setting it, SQLAlchemy might complain if column is missing from metadata or table
                res = Response(data=response, user_id=current_user.id, question_id=question.id)
                db.session.add(res)
                db.session.commit()
            except Exception as e:
                print(f"Warning: Could not save response with question_id (likely missing column): {e}")
                db.session.rollback()
                # Fallback to no question_id
                res = Response(data=response, user_id=current_user.id)
                db.session.add(res)
                db.session.commit()
        except Exception as e:
            print(f"Error occurred during chat save: {e}")
            db.session.rollback()
            
    message={"answer":response}
    return jsonify(message)

@chatbot1.get('/getChatHistory')
def getChatHistory():
    if not current_user.is_authenticated:
        return jsonify([])
    
    try:
        # Get questions and responses sorted by date
        questions = Question.query.filter_by(user_id=current_user.id).order_by(Question.date.asc()).all()
        responses = Response.query.filter_by(user_id=current_user.id).order_by(Response.date.asc()).all()
        
        history = []
        q_idx = 0
        r_idx = 0
        
        # Interleave questions and responses based on timestamp
        while q_idx < len(questions) or r_idx < len(responses):
            if q_idx < len(questions) and r_idx < len(responses):
                if questions[q_idx].date <= responses[r_idx].date:
                    history.append({'name': 'User', 'message': questions[q_idx].data})
                    q_idx += 1
                else:
                    history.append({'name': '3bas', 'message': responses[r_idx].data})
                    r_idx += 1
            elif q_idx < len(questions):
                history.append({'name': 'User', 'message': questions[q_idx].data})
                q_idx += 1
            else:
                history.append({'name': '3bas', 'message': responses[r_idx].data})
                r_idx += 1
                
        return jsonify(history)
    except Exception as e:
        print(f"Failed to load chat history: {e}")
        return jsonify([{"name": "3bas", "message": "System: Unable to load history from database."}])
