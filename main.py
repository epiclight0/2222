import datetime
import json
import requests, jsonify
import sys
import logging
import os
from flask import Flask,render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from models import User, Post
from datetime import datetime
from werkzeug.urls import url_parse
from forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, Datareq, Deletepost
from task import urlf

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]
db_host = os.environ["DB_HOST"]

# Extract host and port from db_host
host_args = db_host.split(":")
db_hostname, db_port = host_args[0], int(host_args[1])

pool = SQLAlchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
    SQLAlchemy.engine.url.URL.create(
        drivername="mysql+pymysql",
        username=db_user,  # e.g. "my-database-user"
        password=db_pass,  # e.g. "my-database-password"
        host=db_hostname,  # e.g. "127.0.0.1"
        port=db_port,  # e.g. 3306
        database=db_name,  # e.g. "my-database-name"
    ),
    **db_config
)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

#@app.before_request
#def before_request():
#    if current_user.is_authenticated: 
#        current_user.last_seen = datetime.utcnow()
#        db.session.commit()
# current_user from Flask-Login 
# can be used at any time during the handling to 
# obtain the user object that represents the client of the request

@app.route('/',methods=['GET', 'POST'])
@app.route('/index',methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        url = form.url.data
        post = Post(body=form.post.data, url=form.url.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        tables = urlf.get_url(url)
        session["data"] = tables
        if session["data"] == "NO DATA FROM GOOGLE ANALYTICS":
            return redirect(url_for('errors', url = url, anerror = tables,body = form.post.data))
        else:
            flash('Your post is now live!')
            return redirect(url_for('post', body=form.post.data))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Home', form = form,posts=posts, user = current_user,pagename="Welcome")
# @login_required from Flask-login
# function becomes protected and will not allow access to users that are not authenticated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form,pagename = "Login")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form,pagename = "Register")


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    cur_user_id = user.id
    posts = Post.query.filter_by(user_id = cur_user_id).all()
    return render_template('user.html', user=user, posts=posts,pagename="My profile")


@app.route('/post/<body>', methods=['GET', 'POST'])
@login_required
def post(body):
    form = Datareq()
    form1 = Deletepost()
    cuser = current_user.id # get id in the table of current logged user
    posts = Post.query.filter_by(body = body).all() # queery from db.post filtering by user_id equals curent logged in user
    sdsa = session["data"]
    if form.submit.data and form.validate():
        Post.query.filter_by(body = body).update({"datai": sdsa})
        db.session.commit()
        flash('Succes')
        redirect(url_for('project', body=body))
    if form1.submit1.data and form1.validate():
        Post.query.filter_by(body=body).delete()
        db.session.commit()
        session.pop("data", None)    
        return redirect(url_for('index'))
    return render_template('project.html', title='Edit Profile', posts=posts, datau=sdsa,form=form, form1=form1, pagename="Result")

@app.route('/project/<body>', methods=['GET', 'POST'])
@login_required
def project(body):
    session.pop("data", None)    
    cuser = current_user.id # get id in the table of current logged user
    posts = Post.query.filter_by(body = body).all() # queery from db.post filtering by user_id equals curent logged in user
    allpostdata = Post.query.filter_by(body = body).first()
    datai = allpostdata.datai
    timestamp = allpostdata.timestamp
    return render_template('project.html', title='Project', posts=posts, datau=datai,pagename="Project", timestamp = timestamp)

@app.route('/error', methods=['GET', 'POST'])
@login_required
def errors():
    url = request.args.get("url") 
    anerror = request.args.get("anerror")
    body = request.args.get("body")
    session.pop("data", None)
    Post.query.filter_by(body=body).delete()
    db.session.commit()
    return render_template('error.html', url = url, anerror = anerror, pagename = "Oops...")

@app.route('/instruction')
def instruction():
    return render_template('instruction.html', pagename = "Instructions")


    
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_render_template]
# [END gae_python38_render_template]
