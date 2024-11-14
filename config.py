import os

class Config:
    SECRET_KEY = 'xas'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///home_service_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False