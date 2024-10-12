# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '691cf231d8dd19885b1492889269c6edef8ae922'
    STRAVA_CLIENT_ID = '76206'
    STRAVA_CLIENT_SECRET = '691cf231d8dd19885b1492889269c6edef8ae922'
    STRAVA_REDIRECT_URI = 'http://localhost:5000/strava_callback'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///strava_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
