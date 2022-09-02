from sqlalchemy import desc
from sqlalchemy.orm import relationship
import requests
import click
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from datetime import datetime

from bloggr import db


##CONFIGURE TABLES

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")

    @staticmethod
    def get_posts(by_author:str = None):
        if by_author:
            return BlogPost.query.filter_by(name=by_author).order_by(desc(BlogPost.id)).all()
        else:
            return BlogPost.query.order_by(desc(BlogPost.id)).all()

    def add(self):
        db.session.add(self)
        db.session.commit()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    comments = relationship("Comment", back_populates="author")
    posts = relationship("BlogPost", back_populates="author")

    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password
        }

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.Text, nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()
    
# import some blog posts - as part of init
def load_posts():
    blog_url = 'https://theclementsfirm.com//wp-json/wp/v2/posts'
    resp = requests.get(blog_url)
    resp.raise_for_status()
    post_json = resp.json()

    
    db.drop_all()
    db.create_all()
    
    noah = User(
        email="noahclements@gmail.com",
        name="Noah Clements",
        password=generate_password_hash("BubbaLubba1!", salt_length=8)
    )
    db.session.add(noah)
    db.session.commit()
    caroline = User(
        email="clementscaroline@yahoo.com",
        name="Caroline Clements",
        password=generate_password_hash("BubbaLubba2!", salt_length=8)
    )
    db.session.add(noah)
    db.session.commit()

    authors = {
        caroline.name: caroline,
        noah.name: noah
    }
    
    for post in post_json:
        img = post['uagb_featured_image_src']['full']
        if img:
            img_0 = img[0]
        else:
            img_0 = ''

        subtitle = post['uagb_excerpt']
        if subtitle is None:
            subtitle = ""

        author = authors[post['uagb_author_info']['display_name']]
            
        blog_post = BlogPost(
            id=int(post['id']),
            author_id=author.id,
            author=author,
            title=post['title']['rendered'],
            subtitle=subtitle,
            date=datetime.strptime(post['date'], "%Y-%m-%dT%H:%M:%S").strftime("%B %d, %Y"),
            body=post['content']['rendered'],
            img_url=img_0
        )
        try:
            db.session.add(blog_post)
            db.session.commit()
        except:
            pass
# only need to do this on first load, if dropped and created tables.    
# load_posts()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()
    load_posts()
    click.echo('Initialized the database.')

def init_app(app):
    # app.teardown_appcontext(db.session.close_db)
    app.cli.add_command(init_db_command)
    with app.app_context():
        db.drop_all()
        db.create_all()
        load_posts()