import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["spotify_songs"]
songs_collection = db["songs"]

all_songs = songs_collection.find().limit(100)

song = songs_collection.find_one()

happy_songs = songs_collection.find({
        "danceability": { "$gte": '0.6' },
        "energy": { "$gte": '0.6' },
        "valence": { "$gte": '0.6' }
    }, {
         "_id": 0,
         "artist_name": 1, 
         "track_name": 1
    }).limit(10)


sad_songs = songs_collection.find({
    "energy": { "$lte": '0.4' },
    "valence": { "$lte": '0.4' }
}, {
        "_id": 0,
        "artist_name": 1, 
        "track_name": 1
}).limit(10)

energized_songs = songs_collection.find({
    "energy": { "$gte": '0.6' },
    "tempo": { "$gte": '120' }
}, {
        "_id": 0,
        "artist_name": 1, 
        "track_name": 1
}).limit(10)

tired_songs = songs_collection.find({
    "energy": { "$lte": '0.4' }
}, {
        "_id": 0,
        "artist_name": 1, 
        "track_name": 1
}).limit(10)

print("happy songs")
for song in happy_songs:
    print(song)

print("sad songs")
for song in sad_songs:
    print(song)

print("energized songs")
for song in energized_songs:
    print(song)

print("Tired songs")
for song in tired_songs:
    print(song)