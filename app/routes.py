from app import app, db, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from app.models import Users, Posts, Comments, Subscribers
from werkzeug.security import generate_password_hash, check_password_hash
import email_validator
from send_mail import send_message
from random import sample
from werkzeug.utils import secure_filename
from web_forms import RegForm
from parsing import Parser
from flask import render_template, request, redirect, session, url_for
import os

db.create_all()


@app.route('/')
@app.route('/home')
def home():
    return render_template('home_page.html', session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        passw = request.form['password']
        if user and passw:
            data = Users.query.filter_by(username=user).first()
            if data:
                if data.verified:
                    true_password = data.password
                    print(true_password)
                    if check_password_hash(true_password, passw):
                        session['user'] = user
                        return redirect(url_for('home'))
                else:
                    true_password = data.password
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

            if user and passw and email and \
                    len(user) <= 30 and len(email) <= 30:
                if email_validator.validate_email(email):
                    data = Users.query.filter_by(username=user).first()
                    if not data:
                        code = ''.join(sample(['1', '2', '3', '4', '5', '6', '7', '8', '9'], 6))
                        new_user = Users(username=user, password=passw, email=email,
                                         verified=False, code=code, avatar='default_avatar.jpg')
                        db.session.add(new_user)
                        db.session.commit()
                        session['user-to-ver'] = user
                        new_user.send_code()
                        return redirect(url_for('verification'))
                    return render_template('registration.html', title='Sign In', form=form)
                else:
                    return render_template('registration.html', title='Sign In', form=form)
        except email_validator.EmailSyntaxError:
            return redirect(url_for('register', title='Sign In', form=form))
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
        text = request.form['post']
        post_name = request.form['post-name']
        file = request.files['file']
        print(request.files)
        if post_name and text and len(post_name) <= 20 and len(text) <= 600:
            if allowed_file(file.filename):
                    data = Users.query.order_by(Users.id).first()
                    filename = str(data.id + secure_filename(file.filename))
                    print(filename)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    new_post = Posts(postname=post_name, post=text, username=session['user'],
                                     image=filename)
                    db.session.add(new_post)
                    db.session.commit()
            else:
                new_post = Posts(postname=post_name, post=text, username=session['user'],
                                 image=' ')
                db.session.add(new_post)
                db.session.commit()
            return redirect(url_for('user_profile', username=session['user']))
        else:
            return redirect(url_for('create_post'))
    else:
        if 'user' in session:
            return render_template('create_post.html')
        return redirect(url_for('login'))


@app.route('/our_posts')
def our_posts():
    if 'user' in session:
        data = Posts.query.all()
        if not data:
            data = []
        ids = [str(i.id) for i in data]
        posts = [i.post for i in data]
        users = [i.username for i in data]
        images = [i.image for i in data]
        post_names = [i.postname for i in data]
        return render_template('our_posts.html', posts=posts, posts_len=len(posts), users=users,
                               images=images, ids=ids, post_names=post_names, session=session)
    else:
        return redirect(url_for('login'))


@app.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == "POST":
        code = request.form['ver']
        username = session['user-to-ver']
        print('code -', code)
        print(type(username))
        data = Users.query.filter_by(username=username, verified=False).first()
        print(data)
        if data:
            if data.code == code:
                Users.query.filter_by(username=username).update({'verified': True})
                db.session.commit()
                session['user'] = session['user-to-ver']
                print(f'Verified new user - {session["user"]}')
                return redirect(url_for('home'))
        return render_template('verification.html')
    else:
        if 'user' in session or 'user-to-ver' not in session:
            return redirect(url_for("home"))
        return render_template('verification.html')


@app.route('/user/<username>')
def user_profile(username):
    user = Users.query.filter_by(username=username, verified=True).first()
    if user and 'user' in session:
        data = Posts.query.filter_by(username=username).all()
        if not data:
            data = []
        posts = [i.post for i in data]
        images = [i.image for i in data]
        post_names = [i.postname for i in data]
        ids = [i.id for i in data]
        subs = [i.subscriber for i in Subscribers.query.filter_by(username=username).all()]
        subs2 = [i.username for i in Subscribers.query.filter_by(subscriber=username).all()]
        if not subs:
            subs = ()
        avatar = user.avatar
        return render_template('profile.html', user=username, posts=posts, posts_len=len(posts),
                               avatar=avatar, images=images, session=session,
                               post_names=post_names, ids=ids, s_len=str(len(subs)), subs=subs, s2_len=str(len(subs2)))
    else:
        if 'user' in session:
            return '<h1>Такого пользователя не существует</h1>'
        else:
            return redirect(url_for('login'))


@app.route('/user/<username>/edit', methods=['GET', 'POST'])
def edit_profile(username):
    data = Users.query.filter_by(username=username, verified=True).first()
    if data and 'user' in session:
        if request.method == "POST":
            old_email = data.email
            user = request.form['username']
            passw = request.form['password']
            email = request.form['email']
            file = request.files['file']
            try:
                print((session['user'] == user))
                if user and passw and email and len(user) <= 30 and len(email) <= 30:
                    code = ''.join(sample(['1', '2', '3', '4', '5', '6', '7', '8', '9'], 6))
                    if email_validator.validate_email(email):
                        if file and allowed_file(file.filename):
                            filename = 'username-' + secure_filename(file.filename)
                            print(filename)
                            file.save(os.path.join(UPLOAD_FOLDER, filename))
                            Users.query.filter_by(username=username).update(
                                {'username': user,
                                 'password': generate_password_hash(passw),
                                 'email': email,
                                 'avatar': filename,
                                 'code': code,
                                 'verified': False
                                 }
                            )
                        else:
                            Users.query.filter_by(username=username).update(
                                {'username': user,
                                 'password': generate_password_hash(passw),
                                 'email': email,
                                 'avatar': 'default_avatar.jpg',
                                 'code': code,
                                 'verified': False
                                 }
                            )
                        db.session.commit()
                        print(email, old_email)
                        if email == old_email:
                            print('A')
                            Users.query.filter_by(username=user).update({'verified': True})
                            db.session.commit()
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
            new_comment = Comments(
                username=session['user'],
                comment_name=name,
                comment=comment,
                postid=postid,
                                   )
            db.session.add(new_comment)
            db.session.commit()
        return redirect(url_for('post', postid=postid))
    else:
        if 'user' in session:
            postid = str(postid)

            data = Posts.query.filter_by(id=postid).first()
            if data:
                comments = Comments.query.filter_by(postid=postid).all()
                if not comments:
                    comments = []
                comm_users = [i.username for i in comments]
                comment_name = [i.comment_name for i in comments]
                comments = [i.comment for i in comments]
                return render_template('post.html', post=data.post, user=data.username, image=data.image,
                                       comm_users=comm_users, comments=comments,
                                       coms_lenth=len(comments), comment_name=comment_name,
                                       postname=data.postname, id=data.id)
            return '<h1>Такого поста не существует</h1>'
        return redirect((url_for('login')))


@app.route('/delete/post/<postid>')
def delete_post(postid):
    data = Posts.query.filter_by(id=postid).first()
    if data:
        if data.username == session['user']:
            db.session.delete(Posts.query.filter_by(id=postid).first())
            Comments.query.filter_by(id=postid).delete()
            url = request.headers.get("Referer")
            if url:
                return redirect(url)
    return redirect(url_for('home'))


@app.route('/users/<username>/subscribe')
def subscribe(username):
    if 'user' in session:
        u = Users.query.filter_by(username=username, verified=True).first()
        u2 = Subscribers.query.filter_by(subscriber=session['user'], username=username).first()
        if u:
            if not u2 and session['user'] != username:
                new_sub = Subscribers(subscriber=session['user'], username=username)
                db.session.add(new_sub)
                db.session.commit()
            url = request.headers.get("Referer")
            if url:
                return redirect(url)
        return 'Такого пользователя не существует'
    return redirect(url_for('login'))


@app.route('/users/<username>/unsubscribe')
def unsubscribe(username):
    if 'user' in session:
        u = Users.query.filter_by(username=username, verified=True).first()
        u2 = Subscribers.query.filter_by(subscriber=session['user'], username=username).first()
        print(type(u2))
        if u:
            if u2:
                print('a')
                current_session = db.session.object_session(u2)
                current_session.delete(u2)
                current_session.commit()
            url = request.headers.get("Referer")
            if url:
                return redirect(url)
        return 'Такого пользователя не существует'
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
