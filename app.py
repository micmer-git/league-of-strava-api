# app.py
from flask import Flask, redirect, url_for, session, request, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from config import Config
import requests
import time
import json

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'

# Create the database
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_recent_activities(access_token, per_page=5):
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'per_page': per_page,
        'page': 1,
        'before': int(time.time())  # Fetch activities before the current time
    }
    response = requests.get(activities_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    strava_auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={app.config['STRAVA_CLIENT_ID']}&"
        f"response_type=code&"
        f"redirect_uri={app.config['STRAVA_REDIRECT_URI']}&"
        f"approval_prompt=auto&"
        f"scope=read,activity:read"
    )
    return redirect(strava_auth_url)

@app.route('/strava_callback')
def strava_callback():
    code = request.args.get('code')
    if not code:
        return 'Error: No code provided', 400

    token_url = 'https://www.strava.com/oauth/token'
    payload = {
        'client_id': app.config['STRAVA_CLIENT_ID'],
        'client_secret': app.config['STRAVA_CLIENT_SECRET'],
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        return f"Error fetching token: {response.text}", response.status_code

    token_data = response.json()
    athlete = token_data.get('athlete')
    if not athlete:
        return 'Error: No athlete data returned', 400

    user = User.query.filter_by(strava_id=athlete['id']).first()
    if not user:
        user = User(
            strava_id=athlete['id'],
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_expires_at=token_data['expires_at']
        )
        db.session.add(user)
    else:
        user.access_token = token_data['access_token']
        user.refresh_token = token_data['refresh_token']
        user.token_expires_at = token_data['expires_at']
    db.session.commit()

    login_user(user)
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch athlete details
    headers = {'Authorization': f'Bearer {current_user.access_token}'}
    athlete_url = 'https://www.strava.com/api/v3/athlete'
    athlete_response = requests.get(athlete_url, headers=headers)
    if athlete_response.status_code != 200:
        return f"Error fetching athlete data: {athlete_response.text}", athlete_response.status_code

    athlete_data = athlete_response.json()

    # Fetch recent activities
    activities = get_recent_activities(current_user.access_token, per_page=5)

    return render_template('dashboard.html', athlete=athlete_data, activities=activities)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Token Refresh Logic (Optional)
def refresh_token(user):
    token_url = 'https://www.strava.com/oauth/token'
    payload = {
        'client_id': app.config['STRAVA_CLIENT_ID'],
        'client_secret': app.config['STRAVA_CLIENT_SECRET'],
        'grant_type': 'refresh_token',
        'refresh_token': user.refresh_token
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        user.access_token = token_data['access_token']
        user.refresh_token = token_data['refresh_token']
        user.token_expires_at = token_data['expires_at']
        db.session.commit()
    else:
        # Handle error (e.g., force user to re-authenticate)
        logout_user()

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_time = int(time.time())
        if current_user.token_expires_at <= current_time:
            refresh_token(current_user)

if __name__ == '__main__':
    app.run(debug=True)
