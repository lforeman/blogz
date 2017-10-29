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
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
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
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) < 3 or len(username) > 20:
            flash("Not a valid username", "error")  

        elif len(password) < 3 or len(password) > 20:
            flash('Not a valid username', 'error')

        elif password != verify:
            flash("Not a valid password", "error")

        else:
            existing_user = User.query.filter_by(username=username).first()

            if existing_user:
                flash("User already exists", "error")
            
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route ('/', methods=['GET', 'POST'])
def index():
    users = User.query.all()

    return render_template('index.html', title="Blogz Users", users=users)



@app.route ('/blog', methods=['GET', 'POST'])
def blog_list():
    
    
    if request.args.get('id'):
        blog_id = request.args.get("id")
        blog = Blog.query.get(blog_id)

        return render_template('singleBlogEntry.html', blog=blog)
    
    elif request.args.get('user'):
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner=user).all()
        
        return render_template('singleUser.html', blogs=blogs)

    else:
        
        blogs = Blog.query.all()

        return render_template('blog.html', title = "Build A Blog", blogs=blogs)

@app.route ('/user', methods=['GET', 'POST'])
def display_user():
    if request.args.get('id'):
        id = request.args.get("id")[0]
        #blog = Blog.query.get(id)
        blogs = Blog.query.filter_by(owner_id=id).all()


        return render_template('singleUser.html', title = "Blogz by User", blogs=blogs)
        

@app.route('/newpost', methods=['GET' , 'POST'])
def add_blog():
    if request.method == 'GET':
        return render_template('newpost.html', title="Add Blog Entry")

    if request.method =='POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ""
        body_error = ""
        owner = User.query.filter_by(username=session['username']).first()

        if len(blog_title) < 1:
            title_error = "Please Enter a Title"

        if len(blog_body) < 1:
            body_error = "Please Enter a Blog" 

        if not title_error and not body_error:
            blog = Blog(blog_title, blog_body, owner) 
            db.session.add(blog)
            db.session.commit()
            query_param_url= "/blog?id=" + str(blog.id)
            return redirect(query_param_url)

        else:
            return render_template('newpost.html', title="Add Blog Entry", title_error=title_error, body_error=body_error )      

if __name__=='__main__':
    app.run()
