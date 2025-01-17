from socket import gethostname
from flaskapp import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    if 'liveconsole' not in gethostname():
        app.run(debug=True)
