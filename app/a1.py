import nltk
import heapq  
import os
import re
nltk.download('punkt')
import math
nltk.download('stopwords')
nltk.download('wordnet')
import operator
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize,word_tokenize
nltk.download('averaged_perceptron_tagger')
from random import randint
from time import strftime
from flask import Flask, render_template, send_file,flash, request
from wtforms import Form, TextField, validators, StringField, SubmitField
Stopwords = set(stopwords.words('english'))
wordlemmatizer = WordNetLemmatizer()
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])


def get_time():
    time = strftime("%Y-%m-%dT%H:%M")
    return time

def write_to_disk(name,output):
    data = open('file.log', 'a')
    timestamp = get_time()
    data.write('DateStamp={}, Input={},Output={} \n'.format(timestamp, name,output))
    data.close()


def lemmatize_words(words):
    lemmatized_words = []
    for word in words:
       lemmatized_words.append(wordlemmatizer.lemmatize(word))
    return lemmatized_words
def stem_words(words):
    stemmed_words = []
    for word in words:
       stemmed_words.append(stemmer.stem(word))
    return stemmed_words
def remove_special_characters(name):
    regex = r'[^a-zA-Z0-9\s]'
    name = re.sub(regex,'',name)
    return name
def freq(words):
    words = [word.lower() for word in words]
    dict_freq = {}
    words_unique = []
    for word in words:
       if word not in words_unique:
           words_unique.append(word)
    for word in words_unique:
       dict_freq[word] = words.count(word)
    return dict_freq
def pos_tagging(name):
    pos_tag = nltk.pos_tag(name.split())
    pos_tagged_noun_verb = []
    for word,tag in pos_tag:
        if tag == "NN" or tag == "NNP" or tag == "NNS" or tag == "VB" or tag == "VBD" or tag == "VBG" or tag == "VBN" or tag == "VBP" or tag == "VBZ"  or tag == "CC" or tag == "CD" or tag == "DT" or tag == "ES" or tag == "JJ":
             pos_tagged_noun_verb.append(word)
    return pos_tagged_noun_verb
def tf_score(word,sentence):
    freq_sum = 0
    word_frequency_in_sentence = 0
    len_sentence = len(sentence)
    for word_in_sentence in sentence.split():
        if word == word_in_sentence:
            word_frequency_in_sentence = word_frequency_in_sentence + 1
    tf =  word_frequency_in_sentence/ len_sentence
    return tf
def idf_score(no_of_sentences,word,sentences):
    no_of_sentence_containing_word = 0
    for sentence in sentences:
        sentence = remove_special_characters(str(sentence))
        sentence = re.sub(r'\d+', '', sentence)
        sentence = sentence.split()
        sentence = [word for word in sentence if word.lower() not in Stopwords and len(word)>1]
        sentence = [word.lower() for word in sentence]
        sentence = [wordlemmatizer.lemmatize(word) for word in sentence]
        if word in sentence:
            no_of_sentence_containing_word = no_of_sentence_containing_word + 1
    idf = math.log10(no_of_sentences/no_of_sentence_containing_word)
    return idf
def tf_idf_score(tf,idf):
    return tf*idf
def word_tfidf(dict_freq,word,sentences,sentence):
    word_tfidf = []
    tf = tf_score(word,sentence)
    idf = idf_score(len(sentences),word,sentences)
    tf_idf = tf_idf_score(tf,idf)
    return tf_idf
def sentence_importance(sentence,dict_freq,sentences):
     sentence_score = 0
     sentence = remove_special_characters(str(sentence))
     sentence = re.sub(r'\d+', '', sentence)
     pos_tagged_sentence = []
     no_of_sentences = len(sentences)
     pos_tagged_sentence = pos_tagging(sentence)
     for word in pos_tagged_sentence:
          if word.lower() not in Stopwords and word not in Stopwords and len(word)>1:
                word = word.lower()
                word = wordlemmatizer.lemmatize(word)
                sentence_score = sentence_score + word_tfidf(dict_freq,word,sentences,sentence)
     return sentence_score


@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
            #file = 'input.txt'
#file = open(file , 'r')
#name = file.read()
    #print(form.errors)
    if request.method == 'POST':
        name=request.form['name']

        tokenized_sentence = sent_tokenize(name)
        name = remove_special_characters(str(name))
        name = re.sub(r'\d+', '', name)
        tokenized_words_with_stopwords = word_tokenize(name)

        tokenized_words = [word for word in tokenized_words_with_stopwords if word not in Stopwords]
        tokenized_words = [word for word in tokenized_words if len(word) > 1]
        tokenized_words = [word.lower() for word in tokenized_words]
        tokenized_words = lemmatize_words(tokenized_words)
        word_freq = freq(tokenized_words)

        #input_user = int(input('Percentage of information to retain(in percent):'))
        input_user=60
        no_of_sentences = int((input_user * len(tokenized_sentence))/100)
        #print(no_of_sentences)
        c = 1
        sentence_with_importance = {}
        for sent in tokenized_sentence:
            sentenceimp = sentence_importance(sent,word_freq,tokenized_sentence)
            sentence_with_importance[c] = sentenceimp
            c = c+1
        sentence_with_importance = sorted(sentence_with_importance.items(), key=operator.itemgetter(1),reverse=True)
        cnt = 0
        summary = []
        sentence_no = []
        for word_prob in sentence_with_importance:
            if cnt < no_of_sentences:
                sentence_no.append(word_prob[0])
                cnt = cnt+1
            else:
                break
        sentence_no.sort()
        cnt = 1
        for sentence in tokenized_sentence:
            if cnt in sentence_no:
                summary.append(sentence)
            cnt = cnt+1
        summary = " ".join(summary)
        print("\n")
        print("Summary:")
        print(summary)
        outF = open('C:/nlp/app/summary.txt',"w")
        outF.write(summary)

        if form.validate():
        	output=summary
        	write_to_disk(name,output)
        	flash('{}'.format(output)) #pass output varible here

        else:
            flash('Error: All Fields are Required')

    return render_template('index.html', form=form)
@app.route('/download')
def download_file():
	p = 'C:/nlp/app/summary.txt'
	return send_file(p,as_attachment=True)
if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    app.run()
