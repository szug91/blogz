from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask (__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, password):
        self.name = name
        self.password = password

@app.before_request
def require_login():
    disallowed_routes = ['newpost']
    if request.endpoint in disallowed_routes and 'name' not in session:
        return redirect('/login')

@app.route('/UserBlog', methods=['GET'])
def blog():
    name = request.args['name']
    blogset = Blog.query.filter_by(owner_id=name)
    
    return render_template('blog.html', head="Blogz!", blogset=blogset )

@app.route('/allposts', methods=['GET'])
def allposts():
    blogset = reversed(Blog.query.all())
    return render_template('blog.html', head="Blogz!", blogset=blogset )

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        verify = request.form['verify']
        error = False
        if name.strip() == '':
            flash("Whats your name MAN!",'error')
            error = True
        if len(name)>=120 or len(name)<=3:
            flash("ladies like length",'error')
            error = True
        if len(password)<=3 or len(password)>=120:
            flash("That's not a valid password",'error')
            error = True
        if password != verify:
            flash("Passwords don't match",'error')
            error = True
        
        if error is False:
            existing_user = User.query.filter_by(name=name).first()
        
            if not existing_user:
                new_user = User(name, password)
                db.session.add(new_user)
                db.session.commit()
                session['name'] = name
                return redirect('/newpost')
            else:
                flash('Ya already been here ya dingus', 'error')
                return render_template('signup.html')
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=name).first()
        if user and user.password == password:
            session['name'] = name
            flash('Logged In')
            return redirect('/')
        else:
            flash('User password is incorrect or user does not exist', 'error')

    return render_template('login.html')

@app.route('/', methods=['GET','POST'])
def index():
    user_list = (reversed(User.query.all()))

    return render_template('index.html', head="Welcome to the blogosphere!", user_list=user_list )

@app.route('/logout')
def logout():
    del session['name']
    return redirect('/login')

@app.route('/newpost', methods=['POST', 'GET'])
def newblog():
    owner = User.query.filter_by(name=session['name']).first()
    title = ''
    body = ''
    title_error = ''
    body_error = ''
    error = False
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title.strip() == '':
            title_error = "Let's make a title!"
            error = True
        if body.strip() == '':
            body_error = "How about a post to go with that beautiful title?"
            error = True
        if error is False:
            blog = Blog(title, body, owner)
            db.session.add(blog)
            db.session.commit()
            blog_id = str(blog.id)    
            return redirect('/blogpost?id='+blog_id)
    
    return render_template('newpost.html', title=title, head="New Blog",
    body=body, title_error=title_error, body_error=body_error)


@app.route('/blogpost', methods=['GET'])
def blogpost():
    id = request.args['id']
    blog = Blog.query.filter_by(id=id).first()
    blog = db.session.query(Blog).filter(Blog.id == id).first()
    return render_template('blogpost.html', head="Blog Post!", blog=blog)

if __name__ == '__main__':
    app.run()