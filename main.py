from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blog:1234@localhost:8889/blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']
        title_error = ''
        blog_error = ''
        if not title and not blog:
            title_error = "Please enter a title"
            blog_error = "Please enter a blog post"
            return render_template('newpost.html', title_error = title_error, blog_error=blog_error)
        elif not blog:
            blog_error = "Please enter a blog post"
            return render_template('newpost.html', blog_error = blog_error, title_content=title)
        elif not title:
            title_error = "Please enter a title for your post"
            return render_template('newpost.html', title_error = title_error, blog_content=blog)
        else:
            new_blog = Blog(title, blog)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?key_id=' + str(new_blog.id))

    return render_template('newpost.html')


@app.route('/blog', methods=['GET', 'POST'])
def blog():

    post_id = request.args.get('key_id')
    if post_id != None:
        post_id = int(post_id)
        blog = Blog.query.filter_by(id=post_id).first()
        return render_template('post.html', title='Build a Blog', blog=blog)
    
    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog", blogs=blogs)



if __name__ == '__main__':
    app.run()
