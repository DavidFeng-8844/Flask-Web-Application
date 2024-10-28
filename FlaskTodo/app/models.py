from app import db
from datetime import date, datetime
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import PickleType

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # Title of the Task
    module_code = db.Column(db.String(8), nullable=False)  # Format like XJCO2011
    description = db.Column(db.Text, nullable=True)  # Description
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.Date, nullable=True)
    importance = db.Column(db.String(20), default='low')  # high, medium, low
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_do_list = db.Column(MutableList.as_mutable(PickleType), default=[])
    soft_delete = db.Column(db.Boolean, default=False)  # Field for soft deletes

    @property
    def is_overdue(self):
        if self.deadline:
            return date.today() > self.deadline and not self.completed
        return False

    def __repr__(self):
        return f"Todo('{self.title}', '{self.module_code}', '{self.completed}', '{self.deadline}', '{self.importance}')"