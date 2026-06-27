import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'change-me-secret-key'

    SQLALCHEMY_DATABASE_URI = (
        'sqlite:///' + os.path.join(BASE_DIR, 'ismds.db')
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')