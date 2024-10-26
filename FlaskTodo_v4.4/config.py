import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flask_todo.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True   

WTF_CSRF_ENABLED = True
SECRET_KEY = 'e683639d1e6795cb015ec777f155e67d'