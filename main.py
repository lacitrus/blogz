from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog')
def blog():
    id = request.args.get('id')  # Get the id from the GET method when after clicking the URL containing id value

    if id:  # Display single entry of blog if requested at the same route
        blog = Blog.query.filter_by(id=id).first() # Get the single entry of blog matched with id
        return render_template('entry.html', blog=blog)
    else:    # Display all blog entries as the second methond to handle the request
        blogs = Blog.query.all() # Get all blogs as list object
        return render_template('blog.html', title = "My blog home", blogs = blogs )

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

    if newtitle == "":
        title_error = "Please fill in the title"
    if newbody == "":
        body_error = "Please fill in the body"

    if title_error or body_error:
        return render_template('newpost.html', title = "Add a blog post", body_error= body_error, title_error=title_error)
    
    # Post the blog entry to the database and redirect the confirmation to the single blog that was created
    elif request.method == 'POST':
                
        newpost = Blog(newtitle, newbody)
        db.session.add(newpost)
        db.session.commit()
        
    #blog = Blog.query.filter_by(title=newtitle).first()
    #id = blog.id
    # The simpler way to get the id of the new blog post 
    id = newpost.id
    return redirect('/blog?id={0}'.format(id) )
    
    
if __name__ == "__main__":
    app.run()
