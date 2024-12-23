from socket import gethostname
from flaskapp import app, db


# def main():
#     app.run(debug=True, port=5000)


# if __name__ == "__main__":
#     main()    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    if 'liveconsole' not in gethostname():
        app.run(debug=True)
    