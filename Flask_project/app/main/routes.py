from flask import session, redirect, url_for, render_template, request, flash
from . import main
from .forms import LoginForm, SignupForm, TwitterForm, ConfigForm
from email.mime.text import MIMEText
from email.header import Header
from email import charset
import os, cgi, cgitb, psycopg2, smtplib
import oauth2 as oauth
import twitter



cgitb.enable()
#postgresql
password="**********************"#your_password
user="**********************"#your_user
database_name = "**********************"

@main.route('/', methods=['GET', 'POST'])
def index():
    """"Login form to enter a pw."""
    form = LoginForm()
    conn = psycopg2.connect("dbname=%s host=localhost port=5432 user=%s password=%s"%(database_name,user,password))
    cur = conn.cursor()
    if form.validate_on_submit():
        session['email'] = form.email.data
        session['pw'] = form.pw.data
        cur.execute("SELECT * FROM login2 WHERE email='%s'"%(session['email']))
        text = cur.fetchall()
        if not text:
            flash('Not found that email')
            return render_template('index.html', form=form)
        elif text[0][1] == session['pw']:
            flash('found that email')
            if text[0][2] == '1':
                flash('Success')
                return redirect(url_for('.chat'))
        else:
            flash('Not match or Please config')
    elif request.method == 'GET':
        form.email.data = session.get('email', '')
        form.pw.data = session.get('pw', '')
    return render_template('index.html', form=form)



@main.route('/signup', methods=['GET', 'POST'])
def signup():
    """"Login form to enter a pw."""
    form = SignupForm()
    conn = psycopg2.connect("dbname=%s host=localhost port=5432 user=%s password=%s"%(database_name,user,password))
    cur = conn.cursor()
    if request.method == 'POST':
        session['email2'] = form.email2.data
        session['pw2'] = form.pw2.data
        cur.execute("SELECT * FROM login2 WHERE email='%s'"%(session['email2']))
        text = cur.fetchall()
        if not text:
            if "@" in form.email2.data and "." in form.email2.data:
                flash("We sent you an email. Please config.") #flash
                cur.execute("INSERT INTO login2 (email,pass,status) VALUES ('%s','%s','%s')"%(str(form.email2.data),str(form.pw2.data),'0'))
                conn.commit()
                me = '****@gmail.com' #your gmail address(~~~@gmail.com)
                passwd = "****" #your gmail password
                you = form.email2.data
                titletext = "easy chat"
                body = "your password is "+session['pw2']+"please config thislink http://127.0.1.5000/config"

                gmsg = MIMEText(body)
                gmsg['Subject'] = titletext
                gmsg['From'] = me
                gmsg['To'] = you

                # Send the message via our own SMTP server.
                s = smtplib.SMTP('smtp.gmail.com',587)
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(me, passwd)
                s.send_message(gmsg)
                s.close()
                return redirect(url_for('.index'))

            else:
                flash("Your email is invalid") #flash
                return render_template('signup.html', form=form)
        else:
            flash("Your email is invalid")
            return render_template('signup.html', form=form)

    elif request.method == 'GET':
        form.email2.data = session.get('email2', '')
        form.pw2.data = session.get('pw2', '')
    return render_template('signup.html', form=form)

@main.route('/twitter', methods=['GET', 'POST'])
def twilogin():

    form = TwitterForm()
    conn = psycopg2.connect("dbname=%s host=localhost port=5432 user=%s password=%s"%(database_name,user,password))
    cur = conn.cursor()
    if request.method == 'POST':
        session['consumer_key'] = form.twiid.data
        session['consumer_secret'] = form.twipw.data
        request_token_url = 'http://twitter.com/oauth/request_token'
        access_token_url = 'http://twitter.com/oauth/access_token'
        authenticate_url = 'http://twitter.com/oauth/authenticate'

        consumer_key = form.twiid.data
        consumer_secret = form.twipw.data
        consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        client = oauth.Client(consumer)
        # reqest_token を取得
        resp, content = client.request(request_token_url, 'GET')
        request_token = dict(parse_qsl(content))
        flash(consumer_key,consumer_secret,consumer,client,resp, content,request_token,)
    else:
        return render_template('index.html', form=form)


@main.route('/config', methods=['GET', 'POST'])
def config():
    """"Login form to enter a pw."""
    form = ConfigForm()
    conn = psycopg2.connect("dbname=%s host=localhost port=5432 user=%s password=%s"%(database_name,user,password))
    cur = conn.cursor()
    if request.method == 'POST':
        session['email4'] = form.email4.data
        session['pw4'] = form.pw4.data
        cur.execute("SELECT * FROM login2 WHERE email='%s'"%(session['email4']))
        text = cur.fetchall()
        if not text:
            flash('Not found that email')
            return render_template('config.html',form=form)
        elif text[0][1] == session['pw4']:
            if "0" in text[0][2]:
                flash('Configed. Please login')
                cur.execute("UPDATE login2 SET status='1' WHERE email='%s'"%(session['email4']))
                conn.commit()
                return redirect(url_for('.index'))
            else:
                flash('Already configed')
                return render_template('config.html',form=form)
        else:
            flash('Not match')
            return render_template('config.html',form=form)
    else:
        flash('Not match')
        return render_template('config.html', form=form)

@main.route('/chat')
def chat():
    """Chat pw. The user's email and pw must be stored in
    the session."""
    email = session.get('email', '')
    pw = session.get('pw', '')
    if email == '' or pw == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', email=email, pw=pw)

def uber():
    return render_template('chat.html')
