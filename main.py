from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP4l'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User', backref='blogs')

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    # blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template("index.html", title = "Home Page", users = users)

@app.route('/login', methods=['POST', 'GET'])    
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and password == user.password:
            session['username'] = username
            return redirect('/newpost')
        else:
            if user:
                flash("Password is incorrect", 'error')
            else: 
                flash("User does not exist", 'error')

    return render_template('login.html')  

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')    
    
    # Use tempalte for error messages
    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify'] 

    field_error = ''
    verify_error = ''
    name_error = ''
    password_error = ''


    if username == '' or password == '' or verify == '':
        field_error = "One or more fields are invalid"
    if verify != password:
        verify_error = "Passwords do not match"
    if len(username) < 3:
        name_error = "Invalid username"
    if len(password) < 3:
        password_error = "Invalid password"
    if field_error or verify_error or name_error or password_error:
        return render_template('signup.html', field_error = field_error,
                verify_error = verify_error, name_error = name_error,
                password_error = password_error)
    
    else:
        if request.method == 'POST': 
                
            existing_user = User.query.filter_by(username=username).first()
        
            if existing_user:
                flash("Username already exists!", 'error')
                return redirect('/signup')  
            elif not existing_user:
        
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')





 
    

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/blog')
   

@app.route('/blog')
def blog():
    id = request.args.get('id')  # Get the id from the GET method when after clicking the URL containing id value
    username = request.args.get('user')

    if id:  # Display single entry of blog if requested at the same route
        blog = Blog.query.filter_by(id=id).first() # Get the single entry of blog matched with id
        user = User.query.filter_by(id=blog.owner_id).first()
        return render_template('entry.html', blog = blog, username = user.username)
    if username:
        users = User.query.filter_by(username=username).all()
        blogs = Blog.query.filter_by(owner_id=users[0].id).all()
        return render_template('blog.html', title =username, blogs = blogs, username = username)

    blogs = Blog.query.all() # Get all blogs as list object
    users = User.query.all()
    return render_template('blogs.html', title = "My blog home", blogs = blogs, users = users)

@app.route('/newpost')
def newpost():

    return render_template('newpost.html', title = "Add a blog post")
    
@app.route('/submit', methods=['POST', 'GET'])    
def submit():
    # For form vailidation
    body_error =""
    title_error =""
    
    newtitle = request.form['title']
    newbody = request.form['body']
    owner = User.query.filter_by(username=session['username']).first()

    

    if newtitle == "":
        title_error = "Please fill in the title"
    if newbody == "":
        body_error = "Please fill in the body"

    if title_error or body_error:
        return render_template('newpost.html', title = "Add a blog post", 
                newtitle = newtitle, newbody= newbody, body_error= body_error, title_error=title_error)
    
    # Post the blog entry to the database and redirect the confirmation to the single blog that was created
    elif request.method == 'POST':
                
        newpost = Blog(newtitle, newbody, owner)
        db.session.add(newpost)
        db.session.commit()
        
    #blog = Blog.query.filter_by(title=newtitle).first()
    #id = blog.id
    # The simpler way to get the id of the new blog post 
    id = newpost.id
    return redirect('/blog?id={0}'.format(id) )
    
    
if __name__ == "__main__":
    app.run()
