from flask import Flask
from flask_sqlalchemy import SQLAlchemy

flask_todo = Flask(__name__)
flask_todo.config.from_object('config')
db = SQLAlchemy(flask_todo)

from app import views # At the end to avoid circular imports
