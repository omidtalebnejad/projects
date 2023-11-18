from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask import redirect, url_for
from datetime import datetime
import os
from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'scret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'media')


@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.form.get('search')
    user_profile = None
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        user_profile = user.user_profile if user else None

    if search_query:
        search_posts = Post.query.filter(
            (Post.title.contains(search_query)) | (Post.author.contains(search_query))).all()
        posts = Post.query.all()
    else:
        search_posts = {}
        posts = Post.query.all()

    posts = sorted(posts, key=lambda x: datetime.strptime(x.date.split()[0], '%Y-%m-%d').strftime('%d-%m-%Y'),
                   reverse=True)

    return render_template('index.html', posts=posts, search_posts=search_posts, user_profile=user_profile)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get(post_id)
    return render_template('post_detail.html', post=post)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fullname = db.Column(db.String(120), nullable=False)  
    user_profile = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(120), nullable=True)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'


@app.route('/register')
def index_page():
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username, password=password).first()

    if user:
        session['username'] = username
        return redirect(url_for('index'))
    else:
        flash('The username or password is incorrect. please try again.', 'error')
        return render_template('login.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    existing_user = User.query.filter_by(username=username).first()
    existing_email = User.query.filter_by(email=email).first()

    if existing_user:
        flash('This username is already taken. Please choose a different username.', 'error')
    if existing_email:
        flash('This email address is already registered. Please use a different email address.', 'error')

    if existing_user or existing_email:
        return redirect(url_for('register'))

    password = request.form.get('password')
    fullname = request.form.get('fullname')
    user_profile = request.form.get('user_profile')

    new_user = User(username=username, password=password, fullname=fullname,
                    email=email, user_profile=user_profile)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/login')
def user_list():
    users = User.query.all()
    return render_template('login.html', users=users)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/add_post', methods=['POST'])
def add_post():
    if 'username' not in session:
        flash('You must be logged in to post', 'error')
        return redirect(url_for('login'))

    username = session['username']
    title = request.form.get('title')
    date = datetime.now().strftime('%Y-%m-%d')
    description = request.form.get('description')
    image = request.form.get('image')  # دریافت لینک تصویر
    content = request.form.get('content')

    new_post = Post(title=title, author=username, date=date, description=description, image=image,
                    content=content)
    db.session.add(new_post)
    db.session.commit()

    flash('The post was successfully registered', 'success')
    return redirect(url_for('index'))


@app.route('/add_post')
def add_post_form():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('add_post.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
