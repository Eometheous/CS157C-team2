# Python standard libraries
import json
import os
import pymongo
import logging
import gradio as gr

# Third-party libraries
from flask import Flask, redirect, request, url_for, render_template, render_template_string, jsonify, Response
from flask_login import UserMixin
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests


# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

#MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["spotify_songs"]
songs_collection = db["songs"]
users_collection = db["users"]

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def create(id_, name, email, profile_pic):
        users_collection.insert_one({"_id": id_, "name": name, "email": email, "profile_pic": profile_pic})

    @staticmethod
    def get(id_):
        user_data = users_collection.find_one({"_id": id_})
        if user_data:
            return User(id_=user_data['_id'], name=user_data['name'], email=user_data['email'], profile_pic=user_data['profile_pic'])
        else:
            return None
        
    def is_active(self):
        return True 


# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from MongoDB
@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    if user:
        logging.info("User loaded: {}".format(user))
        return user
    else:
        logging.warning("User not found for ID: {}".format(user_id))
        return None

# # Define route to render Gradio page
# @app.route("/gradio")
# def render_gradio_page():
#     interface = gr.Interface(search_recipes, [mood_buttons, genre_buttons], "text")
#     return render_template("gradio.html", interface=interface)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template('post_login.html', name=current_user.name, email=current_user.email, profile_pic=current_user.profile_pic)
        # return (
        #     "<p>Hello, {}! You're logged in! Email: {}</p>"
        #     "<p>This is where we have to display the gradio page</p>"
        #     "<div><p>Google Profile Picture:</p>"
        #     '<img src="{}" alt="Google profile pic"></img></div>'
        #     '<a class="button" href="/logout">Logout</a>'.format(
        #         current_user.name, current_user.email, current_user.profile_pic
        #     )
        # )
    else:
        # return '<a class="button" href="/login">Google Login</a>'
        return render_template('login.html')


@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve form data
    mood = request.form['mood']
    genre = request.form['genre']
    artist_name = request.form['artist_name']
    track_name = request.form['track_name']
    
    # Redirect or render a thank you page
    return 'Form submitted successfully!'
    # return render_template('response_template.html', response_content=data(as_text=True))

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400


    # Create or retrieve user from MongoDB
    user = User.get(unique_id)
    if not user:
        User.create(unique_id, users_name, users_email, picture)

    # Log in the user
    login_user(user)
    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# @app.route('/music')
# def gradio_app():
#     # Render the Gradio interface using render_template_string
#     return render_template_string(mood_player.launch())

# gets happy sounding songs
@app.route("/songs/happy")
# @login_required
def get_happy_songs():
    happy_songs = songs_collection.find({
        "danceability": { "$gte": '0.6' },
        "energy": { "$gte": '0.6' },
        "valence": { "$gte": '0.6' }
    }, {
         "_id": 0,
         "artist_name": 1, 
         "track_name": 1
    }).limit(10)
    return jsonify(list(happy_songs))

# gets sad sounding songs
@app.route('/songs/sad')
def sad_songs():
    sad_songs = songs_collection.find({
        "energy": { "$lte": '0.4' },
        "valence": { "$lte": '0.4' }
    }, {
         "_id": 0,
         "artist_name": 1, 
         "track_name": 1
    }).limit(10)
    return jsonify(list(sad_songs))

# gets energized sounding songs
@app.route('/songs/energized')
def energized_songs():
    energized_songs = songs_collection.find({
        "energy": { "$gte": '0.6' },
        "tempo": { "$gte": '120' }
    }, {
         "_id": 0,
         "artist_name": 1, 
         "track_name": 1
    }).limit(10)
    return jsonify(list(energized_songs))

# gets tired sounding songs
@app.route('/songs/tired')
def tired_songs():
    tired_songs = songs_collection.find({
        "energy": { "$lte": '0.4' }
    }, {
         "_id": 0,
         "artist_name": 1, 
         "track_name": 1
    }).limit(10)
    return jsonify(list(tired_songs))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


if __name__ == "__main__":
    app.run(ssl_context="adhoc")

