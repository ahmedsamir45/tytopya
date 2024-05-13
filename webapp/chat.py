import random
import json
import pickle
import numpy as np
import nltk

from nltk.stem import WordNetLemmatizer
from keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents2.json').read())



# paterns
words = pickle.load(open('words.pkl', 'rb'))

# tags 
classes = pickle.load(open('classes.pkl', 'rb'))

model = load_model('chatbot_model.h5')

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
    res = model.predict(np.array([bow]))[0]

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

while True:
    message = input("")
    # Predict the intent of the user's message
    ints = predict_class(message)

    # Get a response based on the predicted intent
    res = get_response(ints, intents)
    print(res)
