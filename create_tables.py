from sqlalchemy import create_engine

con = create_engine("postgres://ttpkdgjdnewrkb:a786345bbea0adbfbe50e4b618a3350ecd1ac8028bd00e34d560e471a7bf5ccb@ec2-54-217-213-79.eu-west-1.compute.amazonaws.com:5432/ddq86s0s5prr5k")
con.set_session(autocommit=True)
cur = con.cursor()


cur.execute('''CREATE TABLE comments (
id SERIAL,
username TEXT,
comment_name TEXT,
comment TEXT,
postid INTEGER
);''')
con.commit()

cur.execute('''CREATE TABLE users (
id SERIAL,
username VARCHAR(30),
password TEXT,
email VARCHAR(100),
verified BOOL,
code VARCHAR(10),
avatar TEXT
);''')
con.commit()

cur.execute('''CREATE TABLE posts (
id SERIAL,
username TEXT,
post TEXT,
image TEXT,
postname TEXT
);''')
con.commit()
