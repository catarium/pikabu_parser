from app import app, db_session, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, login_manager
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

db_session.global_init('app/db/blogs.db')
sess = db_session.create_session()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


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
            data = sess.query(Users).filter_by(username=user).first()
            if data:
                print(session)
                if data.verified:
                    true_password = data.password
                    print(true_password)
                    if check_password_hash(true_password, passw):
                        session['user-id'] = data.id
                        return redirect(url_for('home'))
                else:
                    true_password = data.password
                    print(true_password)
                    if check_password_hash(true_password, passw):
                        session['user-to-ver-id'] = data.id
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
                    data = sess.query(Users).filter_by(username=user).first()
                    if not data:
                        code = ''.join(sample(['1', '2', '3', '4', '5', '6', '7', '8', '9'], 6))
                        new_user = Users(username=user, password=generate_password_hash(passw), email=email,
                                         verified=False, code=code, avatar='default_avatar.jpg')
                        sess.add(new_user)
                        sess.commit()
                        session['user-to-ver-id'] = new_user.id
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
        user = sess.query(Users).filter_by(id=session['user-id']).first()
        if post_name and text and len(post_name) <= 20 and len(text) <= 600:
            if allowed_file(file.filename):
                    data = sess.query(Users).order_by(Users.id).first()
                    filename = str(data.id) + secure_filename(file.filename)
                    print(filename)
                    file.save(f'{UPLOAD_FOLDER}/{filename}')
                    new_post = Posts(postname=post_name, post=text, username=user.username, user_id=user.id,
                                     image=filename)
                    sess.add(new_post)
                    sess.commit()
            else:
                new_post = Posts(postname=post_name, post=text, username=user.username, user_id=user.id,
                                 image=' ')
                sess.add(new_post)
                sess.commit()
            return redirect(url_for('user_profile', id=session['user-id']))
        else:
            return redirect(url_for('create_post'))
    else:
        if 'user-id' in session:
            return render_template('create_post.html')
        return redirect(url_for('login'))


@app.route('/our_posts')
def our_posts():
    print(session)
    if 'user-id' in session:
        data = sess.query(Posts).all()
        if not data:
            data = []
        ids = [str(i.id) for i in data]
        posts = [i.post for i in data]
        users = [sess.query(Users).filter_by(id=i.user_id).first() for i in data]
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
        user_id = session['user-to-ver-id']
        print(user_id)
        print('code -', code)
        data = sess.query(Users).filter_by(id=user_id, verified=False).first()
        print(data)
        if data:
            if data.code == code:
                sess.query(Users).filter_by(id=user_id).update({'verified': True})
                sess.commit()
                session['user-id'] = session['user-to-ver-id']
                print(f'Verified new user - {session["user-id"]}')
                return redirect(url_for('home'))
        return render_template('verification.html')
    else:
        if 'user-id' in session or 'user-to-ver-id' not in session:
            return redirect(url_for("home"))
        return render_template('verification.html')


@app.route('/user/<id>')
def user_profile(id):
    user = sess.query(Users).filter_by(id=id, verified=True).first()
    if 'user-id' in session and user:
        data = sess.query(Posts).filter_by(user_id=id).all()
        if not data:
            data = []
        posts = [i.post for i in data]
        images = [i.image for i in data]
        post_names = [i.postname for i in data]
        ids = [i.id for i in data]
        subs = [i.subscriber for i in sess.query(Subscribers).filter_by(id=id).all()]
        subs2 = [i.id for i in sess.query(Subscribers).filter_by(id=id).all()]
        if not subs:
            subs = ()
        avatar = user.avatar
        return render_template('profile.html', user=user, posts=posts, posts_len=len(posts),
                               avatar=avatar, images=images, session=session,
                               post_names=post_names, ids=ids, s_len=str(len(subs)), subs=subs, s2_len=str(len(subs2)), int=int)
    else:
        if 'user-id' in session:
            return '<h1>Такого пользователя не существует</h1>'
        else:
            return redirect(url_for('login'))


@app.route('/user/<id>/edit', methods=['GET', 'POST'])
def edit_profile(id):
    user = sess.query(Users).filter_by(id=int(id), verified=True).first()
    if 'user-id' in session and user:
        if request.method == "POST":
            old_email = user.email
            username = request.form['username']
            passw = request.form['password']
            email = request.form['email']
            file = request.files['file']
            try:
                if username and passw and email and len(username) <= 30 and len(email) <= 30:
                    code = ''.join(sample(['1', '2', '3', '4', '5', '6', '7', '8', '9'], 6))
                    if email_validator.validate_email(email):
                        if file and allowed_file(file.filename):
                            filename = 'username-' + secure_filename(file.filename)
                            print(filename)
                            file.save(os.path.join(UPLOAD_FOLDER, filename))
                            sess.query(Users).filter_by(id=id).update(
                                {'username': username,
                                 'password': generate_password_hash(passw),
                                 'email': email,
                                 'avatar': filename,
                                 'code': code,
                                 'verified': False
                                 }
                            )
                        else:
                            sess.query(Users).filter_by(username=username).update(
                                {'username': username,
                                 'password': generate_password_hash(passw),
                                 'email': email,
                                 'avatar': 'default_avatar.jpg',
                                 'code': code,
                                 'verified': False
                                 }
                            )
                        sess.commit()
                        print(email, old_email)
                        if email == old_email:
                            print('A')
                            sess.query(Users).filter_by(id=id).update({'verified': True})
                            sess.commit()
                            session['user-id'] = user.id
                            return redirect(url_for('home'))
                        else:
                            print('B')
                            session.pop('user-to-ver-id', None)
                            session['user-to-ver-id'] = user.id
                            send_message(email, code)
                            return redirect(url_for('verification'))
                    else:
                        return redirect(url_for('edit_profile', id=id))
                else:
                    return redirect(url_for('edit_profile', id=id))
            except email_validator.EmailSyntaxError:
                print('skdk')
                return render_template('edit.html')
        else:
            if session['user-id'] == int(id):
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
        user = sess.query(Users).filter_by(id=session['user-id']).first()
        if name and comment:
            new_comment = Comments(
                username=user.username,
                comment_name=name,
                comment=comment,
                postid=postid,
                user_id=user.id
                                   )
            sess.add(new_comment)
            sess.commit()
        return redirect(url_for('post', postid=postid))
    else:
        if 'user-id' in session:
            postid = str(postid)

            data = sess.query(Posts).filter_by(id=postid).first()
            if data:
                comments = sess.query(Comments).filter_by(postid=postid).all()
                if not comments:
                    comments = []
                return render_template('post.html', post=data.post, user=data, image=data.image,
                                       comments=comments,
                                       coms_lenth=len(comments),
                                       postname=data.postname, id=data.id)
            return '<h1>Такого поста не существует</h1>'
        return redirect((url_for('login')))


@app.route('/delete/post/<postid>')
def delete_post(postid):
    data = sess.query(Posts).filter_by(id=postid).first()
    if data:
        if data.username == session['user']:
            sess.query(Posts).delete(id=postid.first())
            sess.query(Comments).filter_by(id=postid).delete()
            url = request.headers.get("Referer")
            if url:
                return redirect(url)
    return redirect(url_for('home'))


@app.route('/users/<id>/subscribe')
def subscribe(username):
    if 'user' in session:
        u = sess.query(Users).filter_by(username=username, verified=True).first()
        u2 = sess.query(Subscribers).filter_by(subscriber=session['user'], username=username).first()
        if u:
            if not u2 and session['user'] != username:
                new_sub = Subscribers(subscriber=session['user'], username=username)
                sess.add(new_sub)
                sess.commit()
            url = request.headers.get("Referer")
            if url:
                return redirect(url)
        return 'Такого пользователя не существует'
    return redirect(url_for('login'))


@app.route('/users/<id>/unsubscribe')
def unsubscribe(id):
    if 'user' in session:
        u = sess.query(Users).filter_by(id=id, verified=True).first()
        u2 = sess.query(Subscribers).filter_by(subscriber=session['user'], id=id).first()
        print(type(u2))
        if u:
            if u2:
                print('a')
                current_session = sess.object_session(u2)
                current_session.delete(u2)
                current_session.commit()
            url = request.headers.get("Referer")
            if url:
                return redirect(url)
        return 'Такого пользователя не существует'
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
