from config import SQLALCHEMY_DATABASE_URI
from flasktodo import db
import os.path

db.create_all()