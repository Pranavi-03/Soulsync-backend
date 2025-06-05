import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///soulsync.db'  # Use SQLite (or change to PostgreSQL/MySQL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
