from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap

from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import relationship
# from sqlalchemy import desc
from flask_login import login_user, LoginManager, login_required, current_user, logout_user

from flask_gravatar import Gravatar
from functools import wraps


from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from bloggr.models import BlogPost, User, Comment, load_posts
from bloggr import create_app, db

app = create_app()
# app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

Bootstrap(app)

# db.create_all()
# load_posts()
##CONNECT TO DB - now done in app factory
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not int(current_user.id) == 1:
             abort(code=403)
        else:
            return function(*args, **kwargs)
    return wrapper
          

@app.route('/')
def get_all_posts():
    posts = BlogPost.get_posts()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name = form.name.data,
            email = form.email.data,
            password = generate_password_hash(form.password.data, method='pbkdf2:sha256',
                                              salt_length=8) 
        )
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
        except:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login')) 
        else:
            return redirect(url_for('get_all_posts'))
    else:
        return render_template("register.html", form=form)
    


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("That email does not exist, please try again.")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                # flash('You were successfully logged in.')
                return redirect(url_for('get_all_posts'))
            else:
                flash("Password incorrect, please try again.")
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(
                author_id = current_user.id,
                post_id = post_id,
                text = form.comment.data
            )
            db.session.add(comment)
            db.session.commit()
        else:
            flash("You need to be logged in to comment. Please log in (or register).")
            return redirect(url_for('login'))

    return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post")
@login_required
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@login_required
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
