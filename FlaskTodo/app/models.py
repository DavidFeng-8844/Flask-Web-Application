from app import db
from datetime import date, datetime
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import PickleType

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(500), index=True, unique=True)
    start_date = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    rent = db.Column(db.Float)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # Title of the Task
    module_code = db.Column(db.String(8), nullable=False)  # Format like XJCO2011
    description = db.Column(db.Text, nullable=True)  # Description
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.Date, nullable=True)
    importance = db.Column(db.String(20), default='low')  # high, medium, low
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_do_list = db.Column(MutableList.as_mutable(PickleType), default=[])
    soft_delete = db.Column(db.Boolean, default=False)  # Field for soft deletes

    @property
    def is_overdue(self):
        if self.deadline:
            return date.today() > self.deadline and not self.completed
        return False

    def __repr__(self):
        return f"Todo('{self.title}', '{self.module_code}', '{self.completed}', '{self.deadline}', '{self.importance}')"