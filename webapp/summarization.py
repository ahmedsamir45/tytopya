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

from webapp.models import Texts,Summaries
from flask import render_template ,request

from webapp import db
from flask_login import current_user
from flask import Blueprint


summarization1 = Blueprint("summarization1",__name__)

@summarization1.route("/summary")
def summary():

    return render_template("summary.html" , title = "summary" ,custom="summary",js="summary" )

@summarization1.post('/predict')
def predict():

    text = request.form.get("mean_radius")
    title = request.form.get("title")
    # abstractive
    text = ''.join(text)
    preprocessed_text = text.strip().replace('\n','')
    
    t5_input_text =  "summarize: "+preprocessed_text
    tokenized_text = tokenizer.encode(t5_input_text,min_length=50,return_tensors='pt', max_length=1500).to(device)
    summary_ids = model.generate(tokenized_text, min_length=50, max_length=300)
    summary_abs = tokenizer.decode(summary_ids[0], skip_special_tokens=True)


    # extractive
    doc=nlp( preprocessed_text )
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
        count = len(Texts.query.filter_by(user_id=current_user.id).all())+1
        text = Texts(data=text, user_id=current_user.id,count=count ,title=title)
        summary = Summaries(abs=summary_abs, ext=summary_ext, user_id=current_user.id ,title=title)
        try:
            
            db.session.add(text)
            db.session.add(summary)
            db.session.commit()
        except Exception as e:
            # Handle the exception, e.g., log the error
            print(f"Error occurred: {e}")


    return render_template("summary.html" , title = "summary" ,custom="summary",js="summary", summary_abs= summary_abs,summary_ext=summary_ext )



