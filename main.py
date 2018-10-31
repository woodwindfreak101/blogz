from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''
        
        existing_user = User.query.filter_by(username=username).first() 
        
        if len(username) < 4 or username == "":
            username_error = 'Invalid username'
            username = ''
        if len(password) < 4 or password == "":
            password_error = 'Invalid password'
            password = '' 
            username = username
        if verify != password:
            verify_error = 'Passwords do not match'
            username = username
            password = ''
            verify = ''
        if existing_user:
            username_error = "User already exist"
            username = ''
        
        if not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.username
            return redirect('/newpost')
        else:
            return render_template('signup.html',title="Signup", username = username, username_error = username_error, password_error = password_error, verify_error = verify_error)    
    
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        username_error = ''
        password_error = ''
        user = User.query.filter_by(username=username).first()
        
        if username == "":
            username_error = 'Invalid username'
            username = ''
        if password == "":
            password_error = 'Invalid password'
            password = '' 
            username = username
        if not user:
            username_error = "Unidentified user, please make an account"   
        if user and user.password != password:    
            password_error = "Incorrect password"   
            username = username 
       
        if not username_error and not password_error: 
            session['user'] = user.username
            # TODO - "remember" that the user has logged in
            flash("Welcome "+ user.username)
            return redirect('/newpost')
        else:
            return render_template('login.html', title="Login", username = username, username_error = username_error, password_error = password_error)

    return render_template('login.html')

@app.route('/blog', methods=['GET'])
def blogs_list():
    post_id = request.args.get("key_id")
    user_id = request.args.get("user_id")
    if post_id != None:
        post_id = int(post_id)
        blog = Blog.query.filter_by(id=post_id).first()
        return render_template('post.html',title="Build a Blog", blog=blog)
    if user_id != None:
        user_id = int(user_id)
        user = User.query.filter_by(id=user_id).first()
        blogs = user.blogs
        return render_template('user_posts.html',title="User Blogs!", blogs=blogs)    
    
    blogs = Blog.query.all()
    return render_template('blog.html',title="Build a Blog", 
        blogs=blogs)

@app.route('/', methods=['GET'])
def index():
    post_id = request.args.get("key_id")
    user_id = request.args.get("user_id")
    if post_id != None:
        post_id = int(post_id)
        blog = Blog.query.filter_by(id=post_id).first()
        return render_template('post.html',title="Build a Blog", blog=blog)
    if user_id != None:
        user_id = int(user_id)
        user = User.query.filter_by(id=user_id).first()
        blogs = user.blogs
        return render_template('user_posts.html',title="User Blogs!", blogs=blogs)    
    
    users = User.query.all()
    return render_template('index.html',title="Blogs users!", 
        users=users)

@app.before_request
def require_login():
    allowed_routes = ['login','blogs_list','signup','index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
   
    allowed_routes = ['login','blog','signup','index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title_error = ''
        blog_error = ''
        title = request.form['title']
        blog = request.form['blog']
        #working on add the owner or username to the new blog
        owner = User.query.filter_by(username=session['user']).first()
        
        if not title and not blog:  
            title_error = "please enter a title" 
            blog_error = "please enter a blog body"
            return render_template('newpost.html', title_error = title_error, blog_error=blog_error)
        elif not blog:  
                blog_error = "please enter a blog body" 
                return render_template('newpost.html', blog_error=blog_error, title_content=title) 
        elif not title:  
                title_error = "please enter a title" 
                return render_template('newpost.html', title_error = title_error, blog_content=blog)            
        else: 
            new_blog = Blog(title, blog, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?key_id=' + str(new_blog.id))
           
        
    return render_template('newpost.html')

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()

# class Blog(db.Model):

#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(120))
#     body = db.Column(db.String(240))
#     owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#     def __init__(self, title, body, owner):
#         self.title = title
#         self.body = body
#         self.owner = owner

# class User(db.Model):

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(120), unique=True)
#     password = db.Column(db.String(120))
#     blogs = db.relationship('Blog', backref='owner')

#     def __init__(self, username, password):
#         self.username = username
#         self.password = password


# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         username_error = ''
#         password_error = ''
#         user = User.query.filter_by(username=username).first()

#         if username == '':
#             username_error = 'Please use a valid username'
#             username = ''
#         if password == '':
#             password_error = 'Please use a valid password'
#             password = ''
#             username = username
#         if not user:
#             username_error = 'Please register your account.'
#         if user and user.password != password:
#             password_error = 'Please enter the correct password'
#             username = username

#         if not username_error and not password_error:
#             session['user'] = user.username
#             #remember logging in
#             flash('welcome ' + user.username)
#             return redirect('/newpost')
#         else:
#             return render_template('login.html', title='Login', username = username, username_error = username_error, password_error = password_error)

#     return render_template('login.html')


# @app.route('/signup', methods=['POST', 'GET'])
# def signup():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         verify = request.form['verify']

#         username_error = ''
#         password_error = ''
#         verify_error = ''

#         existing_user = User.query.filter_by(username=username).first()

#         if len(username) < 3 or username == '':
#             username_error = 'Invalid username'
#             username = ''
#         if len(password) < 3 or password == '':
#             password_error = 'Invalid password'
#             password = ''
#             username = username
#         if verify != password:
#             verify_error = 'You passwords did not match'
#             username = username
#             password = ''
#             verify = ''
#         if existing_user:
#             username_error = "This user already exists"
#             username = ''

#         if not username_error and not password_error and not verify_error:
#             new_user = User(username, password)
#             db.session.add(new_user)
#             db.session.commit()
#             session['user'] = new_user.username
#             return redirect('/newpost')
#         else:
#             return render_template('signup.html', title="Uuser Signup", username=username, username_error=username_error, password_error=password_error)

#     return render_template('signup.html')

# @app.route('/blog', methods=['GET'])
# def blogs_list():
#     post_id = request.args.get('key_id')
#     user_id = request.args.get('user_id')
#     if post_id != None:
#         post_id = int(post_id)
#         blog = Blog.query.filter_by(id=post_id).first()
#         return render_template('post.html',title="Build a Blog",blog=blog)
#     if user_id != None:
#         user_id = int(user_id)
#         user = User.query.filter_by(id=user_id).first()
#         blogs = user.blogs
#         return render_template('user_posts.html',title="User Blogs",blogs=blogs)

#     blogs = Blog.query.all()
#     return render_template('blog.html',title="Build a Blog",blogs=blogs)


# @app.route('/', methods=['GET'])
# def index():
#     post_id = request.args.get('key_id')
#     user_id = request.args.get('user_id')
#     if post_id != None:
#         post_id = int(post_id)
#         blog = Blog.query.filter_by(id=post_id).first()
#         return render_template('post.html',title="Build a Blog",blog=blog)
#     if user_id != None:
#         user_id = int(user_id)
#         user = User.query.filter_by(id=user_id).first()
#         blogs = user.blogs
#         return render_template('user_posts.html',title="User Blogs",blogs=blogs)

#     users = User.query.all()
#     return render_template('index.html',title="Blogs and Users",users=users)


# @app.before_request
# def require_login():
#     allowed_routes = ['login','blogs_list','signup','index']
#     if request.endpoint not in allowed_routes and 'user' not in session:
#         return redirect('/login')

# @app.route('/newpost', methods=['POST', 'GET'])
# def new_post():

#     allowed_routes = ['login','blog','signup','index']
#     if request.endpoint not in allowed_routes and 'user' not in session:
#         return redirect('/login')
    
#     if request.method == 'POST':
#         title_error = ''
#         blog_error = ''
#         title = request.form['title']
#         blog = request.form['blog']
#         #Owner and username to blog?
#         owner = User.query.filter_by(username=session['user']).first()

#         if not title and not blog:
#             title_error = "Please enter a title"
#             blog_error = "Please write a blog post"
#             return render_template('newpost.html', title_error=title_error,blog_error=blog_error)
#         elif not blog:
#             blog_error = "Please write a blog post"
#             return render_template('newpost.html',blog_error=blog_error,title_content=title)
#         elif not title:
#             title_error = "Please enter a title"
#             return render_template('newpost.html',title_error=title_error,blog_content=blog)
#         else:
#             new_blog = Blog(title, blog, owner)
#             db.session.add(new_blog)
#             db.session.commit()
#             return redirect('/blog?key_id=' + str(new_blog.id)) 


#         return render_template('newpost.html') 

# @app.route('/logout', methods=['POST'])
# def logout():
#     del session['user']
#     return redirect('/blog')


# if __name__ == '__main__':
#     app.run()


    # if request.method == 'POST':
    #     title = request.form['title']
    #     blog = request.form['blog']
    #     title_error = ''
    #     blog_error = ''
    #     if not title and not blog:
    #         title_error = "Please enter a title"
    #         blog_error = "Please enter a blog post"
    #         return render_template('newpost.html', title_error = title_error, blog_error=blog_error)
    #     elif not blog:
    #         blog_error = "Please enter a blog post"
    #         return render_template('newpost.html', blog_error = blog_error, title_content=title)
    #     elif not title:
    #         title_error = "Please enter a title for your post"
    #         return render_template('newpost.html', title_error = title_error, blog_content=blog)
    #     else:
    #         new_blog = Blog(title, blog)
    #         db.session.add(new_blog)
    #         db.session.commit()
    #         return redirect('/blog?key_id=' + str(new_blog.id))

    # return render_template('newpost.html')


# @app.route('/blog', methods=['GET', 'POST'])
# def blog():

#     post_id = request.args.get('key_id')
#     if post_id != None:
#         post_id = int(post_id)
#         blog = Blog.query.filter_by(id=post_id).first()
#         return render_template('post.html', title='Build a Blog', blog=blog)
    
#     blogs = Blog.query.all()
#     return render_template('blog.html', title="Build a Blog", blogs=blogs)


# #@app.route('/signup')

# @app.route('/signup')
# def display_user_signup():
#     return render_template('signupform.html')
# #.format(username='',username_error='',user_password='',user_password_error='',verify_user_password='',
# #verify_password_error='',user_email='',user_email_error='')

# def correct_length(text):
#     if len(text) > 3 and len(text) <= 20 and " " not in text:
#         return True
#     else:
#         return False

# def passwords_match(text, text2):
#     if text == text2:
#         return True
#     else:
#         return False

# def proper_email(email):
#     if "." in email and "@" in email:
#         if correct_length(email):
#             return True
#         else: 
#             return False
#     else:
#         return False 

# @app.route('/signup', methods=['POST'])
# def validate_user():

#     username = request.form['username']
#     user_password = request.form['user_password']
#     verify_user_password = request.form['verify_user_password']
#     user_email = request.form['user_email']

#     user_password_error = ''
#     username_error = ''

#     if not correct_length(username):
#         username_error = "Username must be between 4 and 20 characters long, and cannot have spaces."
#         username=''
#         return render_template('signup_form.html',username_error=username_error,username=username)

#     if not correct_length(user_password):
#         user_password_error = "Your password must be between 4 and 20 characters long, and cannot contain spaces."
#         user_password=''
#         return render_template('signup_form.html',user_password_error=user_password_error,user_password=user_password,user_email=user_email,username=username)

#     if not passwords_match(user_password, verify_user_password):
#         user_password_error = "Your passwords must match exactly, be between 4 and 20 characters long, and cannot have spaces."
#         user_password=''
#         verify_user_password=''
#         return render_template('signup_form.html',user_password_error=user_password_error,user_password=user_password,verify_user_password=verify_user_password,user_email=user_email,username=username)

#     if not user_email == '':
#         if not proper_email(user_email):
#             user_email_error = "please have between 4 and 20 characters in your email, one period and one @ in your email."
#             user_email=''
#             return render_template('signup_form.html',user_email_error=user_email_error,user_email=user_email,username=username)
#         else: 
#             return render_template('welcome_username.html',username=username)
#                 #'signup_form.html',username=username,username_error=username_error,password='',
#                 #user_password_error=user_password_error,verify_password='',user_email='',user_email_error='')
#     else:
#         return render_template('welcome_username.html',username=username)


# #@app.route('/login')

# #@app.route('/index')

# #def logout post request to /logout redirects to /blog deleting username from session

# #User class


# if __name__ == '__main__':
#     app.run()
