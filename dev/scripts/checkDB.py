import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["spotify_songs"]
songs_collection = db["songs"]

print(songs_collection.find_one())