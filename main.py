from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        if not user:
            flash('User does not exist', 'error')
        elif user.password != password:
            flash('Password is incorrect', 'error')
            

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        error_present = False
        existing_user = User.query.filter_by(username=username).first()

        if not username or len(username) < 3 or len(username)>20 or ' ' in username:
            flash('Please enter a valid username!', 'error') 
            username = ''
            error_present= True

        elif not password or len(password) < 3 or len(password)>20 or ' ' in password:
            flash('Please enter a valid password!', 'error')
            error_present= True

        elif password != verify:
            flash("Passwords don't match!!!", 'error')
            error_present= True

        elif username and existing_user:
            flash('User already exists!', 'error')
            error_present = True

        if not existing_user and not error_present:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    
        else:
            password = ''
            verify = ''
            username = username
            

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods = ['GET'])
def index():
    users = User.query.all()

    id = request.args.get('id')
    blogs = Blog.query.filter_by(owner_id = id).all()

    if id:
        return render_template('singleuser.html', blogs = blogs)
    else:
        return render_template('index.html', users = users)


@app.route('/blog', methods=['GET'])
def list_blogs():
    blogs = Blog.query.all()
    users = User.query.all()

    blog_id = request.args.get('id')
    blog = Blog.query.filter_by(id=blog_id).first()
  

    user_id = request.args.get('user_id')
    user_blogs = Blog.query.filter_by(owner_id = user_id).all()
    
    #display individual post
    if blog_id:
        blog_user = blog.owner_id
        user = User.query.filter_by(id=blog_user).first()
        return render_template('singlepost.html', blog=blog, user=user)
    
    #display single user posts
    elif user_id:
        return render_template('singleuser.html', blogs=user_blogs)

    else: 
        return render_template('blog.html',title="Build A Blog!", 
            blogs=blogs, users=users)
    
  

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        owner_id = owner.id

        if title == "":
            flash("Please enter title!")
            return render_template('newpost.html', body = body)
        if body == "":
            flash("Please enter body!")
            return render_template('newpost.html', title = title)
        
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        blog = Blog.query.filter_by(title=title).first()
        user = User.query.filter_by(id = owner_id).first()

        return render_template('singlepost.html', blog = blog, user = user)

    else: 
        return render_template('newpost.html')

if __name__ == '__main__':
    app.run()
