from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, Datareq, Deletepost
from app.models import User, Post
from app.task import urlf
import json
import requests, jsonify
import sys
import logging


@app.before_request
def before_request():
    if current_user.is_authenticated: 
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
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