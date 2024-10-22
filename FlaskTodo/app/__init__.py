from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

web_blog = Flask(__name__) # __name__ is the name of the module
web_blog.config.from_object('config')
db = SQLAlchemy(web_blog)
migrate = Migrate(web_blog, db)
with web_blog.app_context():
    db.create_all()


from app import views # put it at the end to avoid circular imports
