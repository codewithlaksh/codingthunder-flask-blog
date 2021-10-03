from flask import Flask, render_template, request, redirect, session # pip install flask
from flask_sqlalchemy import SQLAlchemy # pip install flask-sqlalchemy
import math
import json
from datetime import datetime
from flask_wtf.csrf import CSRFProtect # pip install flask-wtf


with open('config.json', 'r') as c:
    params = json.load(c)["params"]


local_server = True
app = Flask(__name__)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
app.secret_key = 'super-secret-key'
db = SQLAlchemy(app)
csrf = CSRFProtect(app)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    slug = db.Column(db.Text(), nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    email = db.Column(db.Text(), nullable=False)
    phone = db.Column(db.Text(), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts']))
    # posts = posts[]
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page - 1) * int(params['no_of_posts']): (page - 1) * int(params['no_of_posts']) + int(
        params['no_of_posts'])]
    if (page == 1):
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif (page == last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)
    return render_template('index.html', posts=posts, prev=prev, next=next)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/post/<string:post_slug>")
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', post=post)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        contact = Contacts(name=name, email=email, phone=phone, message=message, timestamp=datetime.now())
        db.session.add(contact)
        db.session.commit()
        return redirect('/')
    return render_template('contact.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if ('user' in session and session['user'] == params['admin_username']):
        return redirect('/dashboard')
    else:
        if request.method == "POST":
            username = request.form.get('uname')
            password = request.form.get('pass')

            if (username == params['admin_username'] and password == params['admin_password']):
                session['user'] = username
                return redirect('/dashboard')
    return render_template('login.html')


@app.route("/dashboard")
def dashboard():
    if ('user' in session and session['user'] == params['admin_username']):
        posts = Posts.query.filter_by().all()
        last = math.ceil(len(posts) / int(params['no_of_posts']))
        # posts = posts[]
        page = request.args.get('page')
        if (not str(page).isnumeric()):
            page = 1
        page = int(page)
        posts = posts[(page - 1) * int(params['no_of_posts']): (page - 1) * int(params['no_of_posts']) + int(
            params['no_of_posts'])]
        if (page == 1):
            prev = "#"
            next = "/dashboard?page=" + str(page + 1)
        elif (page == last):
            prev = "/dashboard?page=" + str(page - 1)
            next = "#"
        else:
            prev = "/dashboard?page=" + str(page - 1)
            next = "/dashboard?page=" + str(page + 1)
        return render_template('dashboard.html', posts=posts, prev=prev, next=next)
    else:
        return redirect('/login')


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/login')


@app.route("/edit/<string:post_sno>", methods=['GET', 'POST'])
def edit(post_sno):
    if ('user' in session and session['user'] == params['admin_username']):
        if request.method == "POST":
            title = request.form.get('title')
            description = request.form.get('desc')
            slug = request.form.get('slug')

            post = Posts.query.filter_by(sno=post_sno).first()
            post.title = title
            post.description = description
            post.slug = slug
            db.session.commit()
            return redirect('/dashboard')
        post = Posts.query.filter_by(sno=post_sno).first()
        return render_template('edit.html', post=post)
    else:
        return redirect('/login')


@app.route("/edit/post/<string:post_sno>", methods=['GET', 'POST'])
def update(post_sno):
        if request.method == "POST":
            title = request.form.get('title')
            description = request.form.get('desc')
            slug = request.form.get('slug')

            post = Posts.query.filter_by(sno=post_sno).first()
            post.title = title
            post.description = description
            post.slug = slug
            db.session.commit()
            return redirect(f"/edit/{post.sno}")
        else:
            return "<h1>Bad Request (400)</h1>"


@app.route("/addpost", methods=['GET', 'POST'])
def addpost():
    if ('user' in session and session['user'] == params['admin_username']):
        if request.method == "POST":
            title = request.form.get('title')
            description = request.form.get('desc')
            slug = request.form.get('slug')

            post = Posts(title=title, description=description, slug=slug, timestamp=datetime.now())
            db.session.add(post)
            db.session.commit()
            return redirect("/dashboard")
        return render_template('addpost.html')
    else:
        return redirect('/login')


@app.route("/delete/<string:post_sno>")
def deletepost(post_sno):
    if ('user' in session and session['user'] == params['admin_username']):
        post = Posts.query.filter_by(sno=post_sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect("/dashboard")
    else:
        return redirect('/login')


app.run(debug=True)