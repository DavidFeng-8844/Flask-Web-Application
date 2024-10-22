from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

flask_todo = Flask(__name__) # __name__ is the name of the module
flask_todo.config.from_object('config')
# csrf = CSRFProtect(flask_todo)
db = SQLAlchemy(flask_todo)
migrate = Migrate(flask_todo, db)
with flask_todo.app_context():
    db.create_all()


from app import views # put it at the end to avoid circular imports
