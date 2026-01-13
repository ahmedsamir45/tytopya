import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from webapp.models import Texts, Summaries
from flask import render_template, request, Blueprint, flash, jsonify
from webapp import db
from flask_login import current_user
from pypdf import PdfReader
import io

from celery import shared_task
import os

summarization1 = Blueprint("summarization1", __name__, url_prefix='/summary')

@summarization1.route("/")
def summary():
    return render_template("summary.html", title="summary", custom="summary", js="summary")

# Create celery task
@shared_task(bind=True)
def summarize_task(self, raw_text, min_len, max_len, user_id, title, input_type):
    try:
        from transformers import T5Tokenizer, T5ForConditionalGeneration
        import torch
        import spacy
        from spacy.lang.en.stop_words import STOP_WORDS
        from string import punctuation
        from heapq import nlargest
        from webapp import db
        from webapp.models import Texts, Summaries

        # Load models inside task
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model_t5 = T5ForConditionalGeneration.from_pretrained('t5-large')
        tokenizer_t5 = T5Tokenizer.from_pretrained('t5-large')
        model_t5.to(device)

        try:
            nlp = spacy.load('en_core_web_sm')
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load('en_core_web_sm')

        stopwords = list(STOP_WORDS)
        preprocessed_text = raw_text.strip().replace('\n',' ')

        # Abstractive
        t5_input_text = "summarize: " + preprocessed_text
        tokenized_text = tokenizer_t5.encode(t5_input_text, return_tensors='pt', max_length=1500, truncation=True).to(device)
        gen_max_len = max(max_len, min_len + 50)
        
        summary_ids = model_t5.generate(tokenized_text, min_length=min_len, max_length=gen_max_len, num_beams=2, early_stopping=True)
        summary_abs = tokenizer_t5.decode(summary_ids[0], skip_special_tokens=True)

        # Extractive
        doc = nlp(preprocessed_text[:100000]) 
        word_frequencies = {}
        for word in doc:
            if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
                if word.text not in word_frequencies:
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
        
        if word_frequencies:
            max_frequency = max(word_frequencies.values())
            for word in word_frequencies:
                word_frequencies[word] = word_frequencies[word]/max_frequency
        
            sentence_tokens = [sent for sent in doc.sents]
            sentence_scores = {}
            for sent in sentence_tokens:
                for word in sent:
                    if word.text.lower() in word_frequencies:
                        if sent not in sentence_scores:
                            sentence_scores[sent] = word_frequencies[word.text.lower()]
                        else:
                            sentence_scores[sent] += word_frequencies[word.text.lower()]
            
            select_length = max(1, int(len(sentence_tokens) * 0.2))
            summary_ext_sentences = nlargest(select_length, sentence_scores, key=sentence_scores.get)
            summary_ext = ' '.join([word.text for word in summary_ext_sentences])
        else:
            summary_ext = "Could not generate extractive summary."

        # Save to DB (Runs in app context via FlaskTask)
        if user_id:
            new_text = Texts(
                data=raw_text, 
                user_id=user_id, 
                count=len(raw_text.split()), 
                title=title,
                type=input_type
            )
            db.session.add(new_text)
            db.session.flush() 
            
            new_summary = Summaries(
                abs=summary_abs, 
                ext=summary_ext, 
                user_id=user_id, 
                title=title,
                text_id=new_text.id
            )
            db.session.add(new_summary)
            db.session.commit()

        return {
            'status': 'success',
            'summary_abs': summary_abs,
            'summary_ext': summary_ext
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@summarization1.post('/predict')
def predict():
    try:
        title = request.form.get("title")
        raw_text = ""
        user_input_type = request.form.get("inputType", "text")
        
        try:
            min_len = int(request.form.get("min_length", 50))
            max_len = int(request.form.get("max_length", 300))
        except ValueError:
            min_len = 50
            max_len = 300

        if user_input_type == "text":
            raw_text = request.form.get("mean_radius", "") 
        elif user_input_type == "pdf":
            if 'pdf_file' in request.files:
                file = request.files['pdf_file']
                if file.filename != '':
                    pdf_reader = PdfReader(file)
                    for page in pdf_reader.pages:
                        raw_text += page.extract_text() + "\n"
        
        if not raw_text.strip():
             return jsonify({'error': "No text provided"}), 400

        # Trigger Celery Task
        user_id = current_user.id if current_user.is_authenticated else None
        task = summarize_task.delay(raw_text, min_len, max_len, user_id, title, user_input_type)
        
        return jsonify({'task_id': task.id, 'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@summarization1.route('/status/<task_id>')
def get_task_status(task_id):
    from celery.result import AsyncResult
    from flask import current_app
    import json
    
    celery_app = current_app.extensions['celery']
    task_result = AsyncResult(task_id, app=celery_app)
    
    # Build response with proper serialization
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
    }
    
    # Only include result if task is successful
    if task_result.ready():
        if task_result.successful():
            # Get the result - this should be a dict from your task
            task_result_value = task_result.result
            if isinstance(task_result_value, dict):
                result["task_result"] = task_result_value
            else:
                # Handle case where result isn't a dict
                result["task_result"] = {"status": "error", "message": "Unexpected result format"}
        else:
            # Task failed
            result["task_result"] = {
                "status": "error", 
                "message": str(task_result.result) if task_result.result else "Task failed"
            }
    else:
        # Task still pending/running
        result["task_result"] = None
    
    return jsonify(result), 200



