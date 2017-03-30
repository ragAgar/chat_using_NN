from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio
import psycopg2
import datetime
from app.main.seq2seq_my  import Translator#.Translator
from gtts import gTTS
import os, re, twitter, nltk,pickle
import speech_recognition as sr
from pytz import timezone


#twitter developer
auth = twitter.OAuth(consumer_key="**********************", #consumer_key
                     consumer_secret="**********************",#consumer_secret_key
                     token="**********************",#token_key
                     token_secret="**********************")#token_secret_key
t = twitter.Twitter(auth=auth)

#file open
with open('pickles/word_dic.pickle', mode='rb') as f:   word_dic = pickle.load(f)
with open('pickles/bad_word_filter.pickle', mode='rb') as f:  bad_word_filter = pickle.load(f)
word_inv = {v:k for k, v in word_dic.items()}

#postgresql
password="**********************"#your_password
user="**********************"#your_user
database_name = "chat"
conn = psycopg2.connect("dbname=%s host=localhost port=5432 user=%s password=%s"%(database_name,user,password))
cur = conn.cursor()
model_path = "learned/seq2seq_new.model"
model = Translator()
model.load_model(model_path)


@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    pw= session.get('pw')
    join_room(pw)
    emit('status', {'msg': 'You can use function by typing "speech", "twitter"'}, pw=pw)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    pw = session.get('pw')
    usertext = session.get('message')
    auto_text = ""
    if message['msg'] != "":
        emit('message', {'msg':"\t\t\t\t\t\t\t\t\t\t"+message['msg'] + ': ' + "You"}, pw=pw)
        cur.execute("INSERT INTO chat (posted_at,usertext) VALUES (%s,%s)", (str(datetime.datetime.now()),str(message['msg'])))
        conn.commit()

        if auto_text and len(message['msg'])>20:
            X_mini = auto_text
            y_mini = message['msg']
            X_mini = input2X(X_mini,word_dic)
            y_mini = input2X(y_mini,word_dic)
            Translator.updates(True)
        emit('message', {'msg': "Bot"+ ': Understanding...'},pw=pw)
        #print("message",message['msg'])
        auto_text = auto_reply(message['msg'])
        if auto_text:
            emit('message', {'msg': "Bot"+ ': ' + auto_text},pw=pw)

def speech2text():
    # obtain audio from the microphone
    pw = session.get('pw')
    r = sr.Recognizer()
    with sr.Microphone() as source:
        #print("Say something!")
        audio = r.listen(source)
    # recognize speech using Sphinx
    try:
        text = r.recognize_sphinx(audio)
    except sr.UnknownValueError:
        text = ""
        emit('status', {'msg': "Sorry, I couldn't understand ..."}, pw=pw)
    except sr.RequestError as e:
        text = ""
        emit('status', {'msg': 'Sorry, audio is unavailable now...'}, pw=pw)
    return text


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    pw = session.get('pw')
    leave_room(pw)
    modelfile = "learned/seq2seq_new.model"
    model.save_model(modelfile)
    emit('status', {'msg': 'You left the room.'}, pw=pw)


#functions
def search_tweet(from_text):
    from dateutil import parser
    pw= session.get('pw')
    month_dict = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
    print(str(from_text))
    print(len(str(from_text)))
    res = t.search.tweets(q=str(from_text))
    res = res["statuses"]

    for i in range(5):

        datetimes = res[i]['created_at']
        date = parser.parse(datetimes).astimezone(timezone('Asia/Tokyo'))
        if date.month <10: month = '0'+str(date.month)
        else: month = date.month
        if date.day < 10: day = "0"+str(date.day)
        else: day = date.day
        if date.hour < 10: hour = "0"+str(date.hour)
        else: hour = date.hour
        if date.minute < 10: minute = "0"+str(date.minute)
        else: minute = date.minute

        to_text = "\nNo.%s\n[DATE] %s/%s/%s %s:%s\n[USER] %s\n[TEXT] %s"%(i+1,date.year,month,day,hour,minute,res[i]['user']['name'],res[i]['text'])
        emit('message', {'msg': to_text},pw=pw)

def show_timeline():
    from dateutil import parser
    pw= session.get('pw')
    month_dict = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
    res = t.statuses.home_timeline()
    for i in range(5):
        datetimes = res[i]['created_at']
        date = parser.parse(datetimes).astimezone(timezone('Asia/Tokyo'))
        if date.month <10: month = '0'+str(date.month)
        else: month = date.month
        if date.day < 10: day = "0"+str(date.day)
        else: day = date.day
        if date.hour < 10: hour = "0"+str(date.hour)
        else: hour = date.hour
        if date.minute < 10: minute = "0"+str(date.minute)
        else: minute = date.minute
        to_text = "\nNo.%s\n[DATE] %s/%s/%s %s:%s\n[USER] %s\n[TEXT] %s"%(i+1,date.year,month,day,hour,minute,res[i]['user']['name'],res[i]['text'])
        emit('message', {'msg': to_text},pw=pw)

def tweet(from_text):
    t.statuses.update(status=from_text)

#to reply
def input2X(seq,word_dic):
    seq = nltk.word_tokenize(seq.lower())[::-1]
    for s in seq:
        if s not in seq:
            word_dic[s] = word_dic["unk"]
    return seq,word_dic

def adjust_length_X(Xs):
    #PAD ~~~8~12

    if len(Xs)<=5:j_max=5
    elif len(Xs)<=10:j_max=10
    elif len(Xs)<=15:j_max=15
    elif len(Xs)<=20:j_max=20
    else: j_max = round(len(Xs)/5)*5 + 5

    for j in range(j_max - len(Xs)):
        Xs.insert(0,"padd")
    return Xs

def translation(model,inputs,word_dic,bad_word_filter):
    X_test,word_dic2 = input2X(inputs,word_dic=word_dic)
    X_test = adjust_length_X(X_test)
    text_list = []
    for i in range(len(X_test)-1):
        transfred = model.test(X_test[i])
        texts = ""
        for word in transfred:
            if word not in ["stdgo","eos","padd","unk"]:
                texts = texts + " " + word
        text_list.append(texts)
        #print("No.",i," ",text[1].upper()+text[2:])
    #print(text_list)
    texts = bfilter(bad_word_filter=bad_word_filter, text_list=text_list)
    #print("chainer_word",texts)
    return text_list,texts

def bfilter(bad_word_filter,text_list):
    texts = ""
    j = 1
    for i in range(len(text_list)):
        if texts == "":
            for word in nltk.word_tokenize(text_list[-(i+1)]):
                if word in bad_word_filter:
                    j = 0
            if j == 1:
                texts = text_list[-(i+1)]
    if texts == "" or re.sub(re.compile("[!-/:-@[-`{-~]"), '', texts)=="":

        texts = "What's are you saying?"
    #print(texts)
    return texts


#calculator
def text2int(textnum, numwords={}):
    if not numwords:
        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):    numwords[word] = (1, idx)
        for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

        #print(numwords)
        #numwords["minus"] = "-"
        #numwords["plus"] = "+"
        #numwords["divide"] = "/"
        #numwords["times"] = "*"

    current = result = 0
    for word in textnum.split():
        if word not in numwords:

            continue
            #raise Exception("Illegal word: " + word)
        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current#

def calc_w2n(num_text):
    text = ""
    for word in str(num_text).replace("plus",",+,").replace("minus",",-,").replace("devided by",",/,").replace("times",",*,").split(","):
        #print(word)
        if word not in ["+","-","*","/"]:
            try:
                temp = text2int(word)
            except:
                temp = word
            text = text + str(temp)

        else:
            text = text + str(word)
    try:
        result = eval(text)
    except:
        result = "I couldn't calculate!\nPlease tell you calculation again!(ex. ~~ plus ~~)"
    return result,text


#main function auto-reply
def auto_reply(from_text):
    pw= session.get('pw')
    with open('learned/twitter_status.pickle', mode='rb') as f:
        twitter_status = pickle.load(f)
    if from_text=="speech":
        #w= session.get('pw')
        tts = gTTS(text= "Please speak to you microphone!", lang='en')
        tts.save("learned/onsei.mp3")
        os.system("mpg321 learned/onsei.mp3")

        emit('message', {'msg': "Bot"+ ': Recognize your speech...'},pw=pw)
        from_text = speech2text()
        emit('message', {'msg': "Bot"+ ': You said "%s"'%(from_text)},pw=pw)

    #a,b = calc_w2n("one hundred devided by three")
    if "plus" in from_text or "minus" in from_text or "devided by" in from_text or "times" in from_text:
        from_text = re.sub(re.compile("[!-/:-@[-`{-~]"), '', from_text)
        res,texts = calc_w2n(from_text)
        texts = "try to calculate %s, and result was %s"%(texts.replace("*","×").replace("/","÷"),res)
    elif "+" in from_text or "-" in from_text or "÷" in from_text or "×" in from_text:
        try:
            #from_text = from_text.replace("*","×").replace("/","÷")
            from_text_b = from_text.replace("×","*").replace("÷","/")
            res = eval(from_text_b)
            texts = "try to calculate %s, and result was %s"%(from_text,res)
        except:
            text_list,texts = translation(model,from_text,word_dic,bad_word_filter)

    elif from_text =="twitter":
        emit('message', {'msg': "Bot"+ ': What do want to do?\n1: tweet\n2: see timeline\n3: seacrh tweet'},pw=pw)
        texts = ""
        twitter_status = 0
        with open('learned/twitter_status.pickle', mode='wb') as f:
            pickle.dump(twitter_status, f)
    elif from_text == "1":
        emit('message', {'msg': "Bot"+ ': Type your tweet.'},pw=pw)
        twitter_status = 1
        with open('learned/twitter_status.pickle', mode='wb') as f:
            pickle.dump(twitter_status, f)
        texts = ""
    elif from_text == "2":
        emit('message', {'msg': "Bot"+ ': See Timeline(5 tweets)'},pw=pw)
        show_timeline()
        twitter_status = 0
        with open('learned/twitter_status.pickle', mode='wb') as f:
            pickle.dump(twitter_status, f)
        texts = ""
    elif from_text == "3":
        emit('message', {'msg': "Bot"+ ': Type Search Word'},pw=pw)
        twitter_status = 3
        with open('learned/twitter_status.pickle', mode='wb') as f:
            pickle.dump(twitter_status, f)
        texts = ""
    elif twitter_status == 1:
        tweet(from_text)
        emit('message', {'msg': "Bot"+ ': Tweet '+from_text },pw=pw)
        twitter_status = 0
        with open('learned/twitter_status.pickle', mode='wb') as f:
            pickle.dump(twitter_status, f)
        texts = ""
    elif twitter_status == 3:
        emit('message', {'msg': "Bot"+ ': Found tweet!'},pw=pw)
        search_tweet(from_text)
        twitter_status = 0
        with open('learned/twitter_status.pickle', mode='wb') as f:
            pickle.dump(twitter_status, f)
        texts = ""

    else:
        text_list,texts = translation(model,from_text,word_dic,bad_word_filter)
    if texts != "":
        tts = gTTS(text= texts, lang='en')
        tts.save("learned/onsei.mp3")
        os.system("mpg321 learned/onsei.mp3")
    return texts
