# Python standard libraries
import json
import os
import pymongo
import logging
from datetime import datetime

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
user_behavior_collection = db["user_behavior"]
favorites_collection = db["favorites"]

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

    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
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
        favorites_collection_data = favorites_collection.find({"user_id": current_user.id})
        return render_template('post_login.html', name=current_user.name, email=current_user.email, profile_pic=current_user.profile_pic, favorites_collection_data=favorites_collection_data)
    else:
        # return '<a class="button" href="/login">Google Login</a>'
        return render_template('login.html')

def track_user_behavior(user_id, name, mood, genre, search):
    if user_id:
        document = {
            "user_id": user_id,
            "name":name,
            "mood": mood,
            "genre": genre,
            "search": search,
            "timestamp": datetime.now()
        }
        user_behavior_collection.insert_one(document)
        print("added to collection")

def liking_favorite(user_id, trackName, artistName):
    if user_id:
        document = {
            "user_id": user_id,
            "track_name": trackName,
            "artist_name": artistName
        }
        
        # Check if the document already exists
        existing_document = favorites_collection.find_one(document)
        
        if existing_document:
            print("Document already exists in the favorites collection.")
            return False
        else:
            favorites_collection.insert_one(document)
            print("Added to favorites collection")
            return True

@app.route('/dashboard')
def dashboard():
    # Render the dashboard template with dummy history data
    user_behavior_data = user_behavior_collection.find({"user_id": current_user.id}, {"_id": 0,"user_id":0,"name":0})
    print(user_behavior_data)
    favorites_collection_data = favorites_collection.find()
    return render_template('dashboard.html', user_behavior_data=user_behavior_data, favorites_collection_data=favorites_collection_data)
    # return render_template('dashboard.html', history=dummy_history)

@app.route('/favorite', methods=['POST'])
def favorite():
    trackName = request.form['trackName']
    artistName = request.form['artistName']

    if current_user.is_authenticated:
        # Call liking_favorite function with the current user ID
        if liking_favorite(current_user.id, trackName, artistName):
            response = {"status": "success", "message": "Song liked successfully!"}
        else:
            response = {"status": "info", "message": "Song already in favorites."}
    else:
        response = {"status": "error", "message": "You need to be logged in to like songs"}

    # Return the response as JSON
    return jsonify(response), 200 if current_user.is_authenticated else 401

@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve form data
    mood = request.form['mood']
    genre = request.form['genre']
    search = request.form['artist_name']
    # track_name = request.form['track_name']

    if current_user.is_authenticated:
    # Call track_user_behavior function with the current user ID
        track_user_behavior(current_user.id, current_user.name, mood, genre, search)
    else:
        print("user not authorized")
    
    print(f"mood:{mood}")
    print(f"genre:{genre}")
    print(f"search:{search}")
    # print(f"track_name:{track_name}")

    if mood=="search" and genre=="search":
        search_results = songs_collection.find({ "$text": { "$search": search } })
        return render_template('songs.html',songs=search_results[:10])


    if mood=="happy":
        songs = get_happy_songs()
    elif mood=="sad":
        songs = sad_songs()
    elif mood=="energetic":
        songs = energized_songs()
    elif mood=="tired":
        songs = tired_songs()
    else:
        # return "form submitted. no valid function yet"
        songs = songs_collection.find()
    
    if genre=="pop":
        songs = [song for song in songs if song.get('genre') == 'pop'][:10]
    elif genre=="rock":
        songs = [song for song in songs if song.get('genre') == 'rock'][:10]
    elif genre=="hip-hop":
        songs = [song for song in songs if song.get('genre') == 'hip-hop'][:10]
    elif genre=="electronic":
        songs = [song for song in songs if song.get('genre') == 'electronic'][:10]
    elif genre=="jazz":
        songs = [song for song in songs if song.get('genre') == 'jazz'][:10]
    elif genre=="classical":
        songs = [song for song in songs if song.get('genre') == 'classical'][:10]
    else:
        # if genre is NA
        songs = songs[:10]

    print(f"songs = {songs}")


    return render_template('songs.html',songs=songs[:10])
    # Redirect or render a thank you page
    # return 'Form submitted successfully!'
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
         "track_name": 1,
         "genre":1
    })
    # return jsonify(list(happy_songs))
    return happy_songs

# gets sad sounding songs
@app.route('/songs/sad')
def sad_songs():
    sad_songs = songs_collection.find({
        "energy": { "$lte": '0.4' },
        "valence": { "$lte": '0.4' }
    }, {
         "_id": 0,
         "artist_name": 1, 
         "track_name": 1,
         "genre":1
    })
    # return jsonify(list(sad_songs))
    return sad_songs

# gets energized sounding songs
@app.route('/songs/energized')
def energized_songs():
    energized_songs = songs_collection.find({
        "energy": { "$gte": '0.6' },
        "tempo": { "$gte": '120' }
    }, {
         "_id": 0,
         "artist_name": 1, 
         "track_name": 1,
         "genre":1
    })
    # return jsonify(list(energized_songs))
    return energized_songs

# gets tired sounding songs
@app.route('/songs/tired')
def tired_songs():
    tired_songs = songs_collection.find({
        "energy": { "$lte": '0.4' }
    }, {
         "_id": 0,
         "artist_name": 1, 
         "track_name": 1,
         "genre":1
    })
    return jsonify(list(tired_songs))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


if __name__ == "__main__":
    app.run(ssl_context="adhoc",debug=True)

