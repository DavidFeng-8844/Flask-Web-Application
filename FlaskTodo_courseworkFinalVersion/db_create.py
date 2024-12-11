import os
from flask_migrate import init, migrate, upgrade
from app import flask_todo, db
from flask_migrate import Migrate

# Initialize Flask-Migrate
migrate_obj = Migrate(flask_todo, db)


def setup_database():
    """Handles the creation of the database and migrations"""
    with flask_todo.app_context():
        # Check if the migrations directory exists
        if not os.path.exists('migrations'):
            print("No migrations folder found. Initializing migrations...")
            init()  # Initialize the migration folder

        # Run the migration and apply the upgrade
        print("Running migrations...")
        migrate(message="Initial migration")
        print("Applying migrations...")
        upgrade()


if __name__ == "__main__":
    setup_database()
    print("Database setup completed!")
