import pymongo
import csv

def connect_to_db():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    return client["spotify_songs"]

def create_songs_collection(database):
    return database["songs"]

def import_songs_data(collection):
    with open("spotify_data.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            collection.insert_one(row)

def setup_db():
    db = connect_to_db()
    songs_collection = create_songs_collection(db)
    import_songs_data(songs_collection)
    print("Database setup complete")

if __name__ == "__main__":
    setup_db()