import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["spotify_songs"]
songs_collection = db["songs"]

happy_songs = songs_collection.find({
        "danceability": { "$gte": '0.6' },
        "energy": { "$gte": '0.6' },
        "valence": { "$gte": '0.6' }
    }, {
         "_id": 0,
         "artist_name": 1, 
         "track_name": 1
    })
for song in happy_songs:
    print(song)