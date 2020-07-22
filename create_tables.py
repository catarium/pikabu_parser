from sqlalchemy import create_engine

con = create_engine("DATABASE_URL")
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
