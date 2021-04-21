import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# TO_DO IMPLEMENT DATABASE URL = DONE
#SQLALCHEMY_DATABASE_URI = 'postgres://benjaminferkol:lovetrolling@localhost:5432/fyuur'
SQLALCHEMY_DATABASE_URI = 'postgres://benjaminferkol@localhost:5432/fyyur'
