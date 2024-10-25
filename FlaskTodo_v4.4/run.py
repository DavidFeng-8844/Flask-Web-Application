from app import flask_todo
import db_create

db_create.setup_database()
if __name__=="__main__":
        flask_todo.run(debug=True)

