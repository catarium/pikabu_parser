import psycopg2
from flask import Flask, render_template, request, flash, redirect, session, url_for
from flask_wtf import FlaskForm
from parsing import Parser
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import email_validator
from send_mail import send_message
from random import sample
from werkzeug.utils import secure_filename
from web_forms import RegForm
import os


app = Flask(__name__, template_folder='templates')
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdTCbQZAAAAAOSVAPFO_ZfzX9i0qTS4Iub8R3Ru'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdTCbQZAAAAAHx_AZL_TND4HDGMPzdtn5_vNPTj'

con = psycopg2.connect(host='ec2-54-217-213-79.eu-west-1.compute.amazonaws.com',
                       user='ttpkdgjdnewrkb',
                       password='a786345bbea0adbfbe50e4b618a3350ecd1ac8028bd00e34d560e471a7bf5ccb',
                       dbname='ddq86s0s5prr5k')
# con = psycopg2.connect(host='localhost', user='postgres', password='MY_parol', dbname='posts')
con.set_session(autocommit=True)
app.config.from_object(Config)
cur = con.cursor()

#
# command = f"INSERT INTO users (username, password, email) " \
#           f"VALUES('test', '{generate_password_hash('test')}', 'test')"
# cur.execute('DELETE FROM users *')
# cur.execute(command)
# con.commit()


UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# cur.execute('''CREATE TABLE comments (
# id SERIAL,
# username TEXT,
# comment_name TEXT,
# comment TEXT,
# postid INTEGER
# );''')
# con.commit()
#
# cur.execute('''CREATE TABLE users (
# id SERIAL,
# username VARCHAR(30),
# password TEXT,
# email VARCHAR(100),
# verified BOOL,
# code VARCHAR(10),
# avatar TEXT
# );''')
# con.commit()
#
# cur.execute('''CREATE TABLE posts (
# id SERIAL,
# username TEXT,
# post TEXT,
# image TEXT,
# postname TEXT
# );''')
# con.commit()


@app.route('/')
@app.route('/home')
def home():
    return render_template('home_page.html', session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        passw = request.form['password']
        if user != '' and passw != '':
            cur.execute('SELECT username FROM users')
            users_list = cur.fetchall()
            users_list = [i[0] for i in users_list]
            print(users_list)
            if user in users_list:
                command = f"SELECT password, verified FROM users WHERE username = %s;"
                cur.execute(command, (user,))
                data = cur.fetchall()
                if data[0][1]:
                    true_password = data[0][0]
                    print(true_password)
                    if check_password_hash(true_password, passw):
                        session['user'] = user
                        return redirect(url_for('home'))
                else:
                    true_password = data[0][0]
                    print(true_password)
                    if check_password_hash(true_password, passw):
                        session['user-to-ver'] = user
                        return redirect(url_for('verification'))

            return render_template('login.html')
    else:
        if 'user' in session:
            return redirect(url_for("home"))
        return render_template('login.html')


@app.route('/reg', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == "POST":
        user = request.form['username']
        passw = request.form['password']
        email = request.form['email']
        print(user, passw, email)
        try:

            if user != '' and passw != '' and email_validator.validate_email(email) and \
                    len(user) <= 30 and len(email) <= 30:
                cur.execute("SELECT * FROM users WHERE username = %s", (user,))
                if cur.fetchall() == []:
                    code = ''.join(sample(['1', '2', '3', '4', '5', '6', '7', '8', '9'], 6))
                    cur.execute('''INSERT INTO users (username, password, email, verified, code, 
                    avatar)
                    VALUES (
                    %s,
                    %s,
                    %s,
                    False,
                    %s,
                    %s
                    );''', (
                    user, generate_password_hash(passw), email, code, 'default_avatar.jpg'))
                    con.commit()
                    session['user-to-ver'] = user
                    send_message(email, code)
                    return redirect(url_for('verification'))
                return render_template('registration.html')
            else:
                return render_template('registration.html', title='Sign In', form=form)
        except email_validator.EmailSyntaxError:
            return redirect(url_for('registration.html', title='Sign In', form=form))
    else:
        return render_template('registration.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route('/pikabu')
def pikabu():
    parser = Parser()
    posts = parser.parse()
    return render_template('pikabu.html', posts=posts, posts_len=len(posts[1]))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/create-post',  methods=['GET', 'POST'])
def create_post():
    if request.method == "POST":
        try:
            text = request.form['post']
            post_name = request.form['post-name']
            file = request.files['file']
        except KeyError:
            file = None
        print(request.files)
        if file and allowed_file(file.filename) and post_name:
            cur.execute('SELECT id FROM users ORDER BY id DESC LIMIT 1')
            filename = str(cur.fetchall()[0][0]) + secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            command = "INSERT INTO posts (postname, post, username, image) VALUES(%s, %s, %s, %s);"
            cur.execute(command, (post_name, text, session['user'], filename))
            con.commit()
        else:
            command = "INSERT INTO posts (postname, post, username, image) VALUES(%s, %s, %s, %s);"
            cur.execute(command, (post_name, text, session['user'], ' '))
            con.commit()
        return redirect(url_for('user_profile', username=session['user']))
    else:
        if 'user' in session:
            return render_template('create_post.html')
        return redirect(url_for('login'))


@app.route('/our_posts')
def our_posts():
    if 'user' in session:
        cur.execute('SELECT id, username, postname, post, image FROM posts;')
        data = cur.fetchall()
        print(data)
        ids = [str(i[0]) for i in data]
        posts = [i[3] for i in data]
        users = [i[1] for i in data]
        images = [i[4] for i in data]
        post_names = [i[2] for i in data]
        print(posts)
        print(users)
        return render_template('our_posts.html', posts=posts, posts_len=len(posts), users=users,
                               images=images, ids=ids, post_names=post_names, session=session)
    else:
        return redirect(url_for('login'))


@app.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == "POST":
        code = request.form['ver']
        username = session['user-to-ver']
        print(code)
        print(type(username))
        cur.execute('SELECT * FROM users WHERE username = %s AND verified = False;',
                    (username,))
        data = cur.fetchall()
        print(data)
        if data != []:
            print('Bac')
            print(data[0][-1])
            if data[0][-2] == code:
                print('Cab')
                cur.execute('''UPDATE users
                SET verified = true
                WHERE username = %s;
                ''', (username,))
                session['user'] = session['user-to-ver']
                return redirect(url_for('home'))
        return render_template('verification.html')
    else:
        if 'user' in session or 'user-to-ver' not in session:
            return redirect(url_for("home"))
        return render_template('verification.html')


@app.route('/user/<username>')
def user_profile(username):
    cur.execute('SELECT username FROM users WHERE username = %s and verified = true', (username,))
    if cur.fetchall():
        cur.execute('SELECT post, image, postname, id FROM posts WHERE username = %s', (username,))
        data = cur.fetchall()
        posts = [i[0] for i in data]
        images = [i[1] for i in data]
        post_names = [i[2] for i in data]
        ids = [i[3] for i in data]
        cur.execute('SELECT avatar FROM users WHERE username = %s', (username,))
        avatar = cur.fetchall()[0][0]
        print(avatar)
        return render_template('profile.html', user=username, posts=posts, posts_len=len(posts),
                               avatar=avatar, images=images, session=session,
                               post_names=post_names, ids=ids)
    else:
        return '<h1>Такого пользователя не существует</h1>'


@app.route('/user/<username>/edit', methods=['GET', 'POST'])
def edit_profile(username):
    cur.execute('SELECT username FROM users WHERE username = %s and verified = true', (username,))
    if cur.fetchall() and 'user' in session:
        if request.method == "POST":
            cur.execute("SELECT email FROM users WHERE username = %s", (username,))
            old_email = cur.fetchall()[0][0]
            user = request.form['username']
            passw = request.form['password']
            email = request.form['email']
            file = request.files['file']
            cur.execute("SELECT * FROM users WHERE username = %s", (user,))
            try:
                print((session['user'] == user))
                if user and passw and email_validator.validate_email(email) and \
                        (cur.fetchall() == [] or session['user'] == user) and \
                        len(user) <= 30 and len(email) <= 30:
                    code = ''.join(sample(['1', '2', '3', '4', '5', '6', '7', '8', '9'], 6))
                    if file and allowed_file(file.filename):
                        filename = 'username-' + secure_filename(file.filename)
                        print(filename)
                        file.save(os.path.join(UPLOAD_FOLDER, filename))
                        cur.execute('''UPDATE users
                                        SET username = %s,
                                        password = %s,
                                        email = %s,
                                        avatar = %s,
                                        code = %s,
                                        verified = false
                                        WHERE username = %s;
                                        ''', (user, generate_password_hash(passw), email,
                                              filename, code, username,))
                    else:
                        cur.execute('''UPDATE users
                                        SET username = %s,
                                        password = %s,
                                        email = %s,
                                        avatar = %s,
                                        code = %s,
                                        verified = false
                                        WHERE username = %s;
                                        ''', (user, generate_password_hash(passw), email, code,
                                              username,))
                    con.commit()
                    print(email, old_email)
                    if email == old_email:
                        print('A')
                        cur.execute('''UPDATE users
                                        SET verified = true
                                        WHERE username = %s;
                                        ''', (user,))
                        session['user'] = user
                        return redirect(url_for('home'))
                    else:
                        print('B')
                        session.pop('user-to-ver', None)
                        session['user-to-ver'] = user
                        send_message(email, code)
                        return redirect(url_for('verification'))
                else:
                    return redirect(url_for('edit_profile', username=username))
            except email_validator.EmailSyntaxError:
                print('skdk')
                return render_template('edit.html')
        else:
            if session['user'] == username:
                return render_template('edit.html')
            return redirect(url_for('login'))
    else:
        return '<h1>Такого пользователя не существует</h1>'


@app.route('/post/<postid>',  methods=['GET', 'POST'])
def post(postid):
    if request.method == "POST":
        name = request.form['comment-name']
        comment = request.form['comment']
        print('jsadfjasdf', name, comment)
        if name and comment:
            cur.execute('''INSERT INTO comments (username, comment_name, comment, postid)
            VALUES(
            %s,
            %s,
            %s,
            %s
            );''', (session['user'], name, comment, postid))
        return redirect(url_for('post', postid=postid))
    else:
        print('aaaa')
        if 'user' in session:
            postid = str(postid)
            cur.execute('SELECT post, username, image, postname, id FROM posts WHERE id = %s', (postid,))
            data = cur.fetchall()[0]
            if data:
                post, user, image, postname, id_ = data
                cur.execute('SELECT username, comment_name, comment FROM comments WHERE postid = %s', (postid,))
                data = cur.fetchall()
                comm_users = [i[0] for i in data]
                comment_name = [i[1] for i in data]
                comments = [i[2] for i in data]
                return render_template('post.html', post=post, user=user, image=image,
                                       comm_users=comm_users, comments=comments,
                                       coms_lenth=len(comments), comment_name=comment_name,
                                       postname=postname, id=id_)
            return '<h1>Такого поста не существует</h1>'
        return redirect((url_for('login')))


@app.route('/delete/post/<postid>')
def delete_post(postid):
    cur.execute('SELECT post, username, image, postname, id FROM posts WHERE id = %s', (postid,))
    data = cur.fetchall()[0]
    if data:
        if data[1] == session['user']:
            cur.execute('DELETE FROM posts WHERE id = %s', (postid,))
            cur.execute('DELETE FROM comments WHERE postid = %s', (postid,))
            url = request.headers.get("Referer")
            if url:
                return redirect(url)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
