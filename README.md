# chat_using_NN

We use

1. mac os X El capitan
2. python3.5.1
3. psql (PostgreSQL) 9.6.1

## STEP1 Setup

After you installed psql and PostgreSQL.

In terminal.

```Terminal: in terminal
$ psql -d postgres

```

In PostgreSQL
```
postgres=# CREATE DATABASE chat;
postgres=# \c chat

chat=# CREATE TABLE chat(posted_at varchar(40),usertext varchar(100));
chat=# CREATE TABLE login2(email varchar(40),pass varchar(40),status varchar(1));
```

After this you can check this!


```
chat=# \dt
        List of relations
 Schema |  Name  | Type  | Owner 
--------+--------+-------+-------
 public | chat   | table | you
 public | login2 | table | you
(2 rows)
```

## STEP2

After you installed pip.

In terminal.
```command:command
$ pip install -r requirements.txt
```

## STEP3

In terminal.

```Terminal: in terminal
$ cd Flask-SocketIO-Chat
$ python chat.py
```
