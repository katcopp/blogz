from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    completed = db.Column(db.Boolean)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.completed = False


@app.route('/blog', methods=['GET'])
def index():

    blogs = Blog.query.filter_by(completed=False).all()
    
    id = request.args.get('id')
    blog = Blog.query.filter_by(id=id).first()
    
    if not id:
        return render_template('blog.html',title="Build A Blog!", 
            blogs= blogs)
    
    else:
        return render_template('singlepost.html', blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title == "":
            flash("Please enter title!")
            return render_template('newpost.html', body = body)
        if body == "":
            flash("Please enter body!")
            return render_template('newpost.html', title = title)
        
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()
        blog = Blog.query.filter_by(title=title).first()

        return render_template('singlepost.html', blog = blog)

    else: 
        return render_template('newpost.html')

if __name__ == '__main__':
    app.run()
