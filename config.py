import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = False

# Connects to application database.
dbURI = 'postgresql://postgres:postgres@localhost:5432/fyyurapp'
SQLALCHEMY_DATABASE_URI = dbURI
