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