# Chat app with Sequence to Sequence model

## About this repositry

We made Chat web app with flask + Postgresql.

This can return conversation with natural pronaunciation and have Twitter functions using API.

We learned seq2seq model with [Cornell_Movie-Dialogs_Corpus *1](https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html) & chainer.

[demo(youtube)](https://youtu.be/RngCcviQtxk)

## We use

1. mac os X El capitan
2. python3.5.1
3. psql (PostgreSQL) 9.6.1


## STEP 1 : Setup

After you installed psql and PostgreSQL.

In terminal.

```Terminal: in terminal
$ brew install mpg321
$ psql -d postgres

$ git clone https://github.com/ragAgar/chat_using_NN
$ cd chat_using_NN/Flask_project/
```

In PostgreSQL(terminal)
```
postgres=# CREATE DATABASE chat;
postgres=# \c chat

chat=# CREATE TABLE chat(posted_at varchar(40),usertext varchar(100));
chat=# CREATE TABLE login2(email varchar(40),pass varchar(40),status varchar(1));
```

After do these, you can see below!


```
chat=# \dt
        List of relations
 Schema |  Name  | Type  | Owner 
--------+--------+-------+-------
 public | chat   | table | you
 public | login2 | table | you
(2 rows)
```



## STEP 2 : Setup python packages

After you installed pip.

In terminal.
```command:command
$ sudo pip install -r requirements.txt
```

In terminal, download nltk data (book).
```command:command
$ python
>>> import nltk
>>> nltk.download()
```



## STEP 3 : Set Password

In terminal.

```Terminal: in terminal
$ cd Flask-SocketIO-Chat
$ vi routes.py # change password & user & database_name
$ vi events.py # change password & user & database_name
$ python chat.py
```

In routes.py & events.py.
```python:routes.py
password="*******"#your_password
user="*******"#your_user
database_name = "*******"#your database name
```

In routes.py
```
#twitter developer
auth = twitter.OAuth(consumer_key="**********************", #consumer_key
                     consumer_secret="**********************",#consumer_secret_key
                     token="**********************",#token_key
                     token_secret="**********************")#token_secret_key
```



## STEP 4 : Run Server

In terminal.

```Terminal: in terminal
$ cd Flask-SocketIO-Chat
$ python chat.py
```


## Refference
*1 [Cornell_Movie-Dialogs_Corpus](https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html)

*2 [Sequence to Sequence model](https://arxiv.org/abs/1409.3215)

*3 https://github.com/miguelgrinberg/Flask-SocketIO-Chat

*4 http://pika-shi.hatenablog.com/entry/20120210/1328866010

*5 http://tdoc.info/blog/2012/12/05/psycopg2.html

