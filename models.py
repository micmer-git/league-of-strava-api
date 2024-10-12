# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    strava_id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(150), nullable=True)
    firstname = db.Column(db.String(150), nullable=True)
    lastname = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    profile = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    sex = db.Column(db.String(10), nullable=True)
    weight = db.Column(db.Float, nullable=True)
    max_heart_rate = db.Column(db.Integer, nullable=True)
    ftp = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    token_expires_at = db.Column(db.Integer, nullable=False)

    activities = db.relationship('Activity', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.strava_id} - {self.username}>'

class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.BigInteger, unique=True, nullable=False)  # Strava Activity ID
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    distance = db.Column(db.Float, nullable=False)  # in meters
    moving_time = db.Column(db.Integer, nullable=False)  # in seconds
    elapsed_time = db.Column(db.Integer, nullable=False)  # in seconds
    total_elevation_gain = db.Column(db.Float, nullable=True)  # in meters
    start_date_local = db.Column(db.DateTime, nullable=False)
    average_speed = db.Column(db.Float, nullable=True)  # in m/s
    max_speed = db.Column(db.Float, nullable=True)  # in m/s
    average_heartrate = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Activity {self.activity_id} - {self.name}>'
