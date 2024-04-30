# This code converts all the json files into a single dataframe
import pandas as pd
import json

def json_to_dataframe(json_file):
    # Load the JSON data
    with open(json_file) as f:
        data = json.load(f)

    # Extract the playlists section
    playlists = data['playlists']

    # Create a list to store the track attributes
    tracks_attributes = []

    # Loop through each playlist
    for playlist in playlists:
        # Loop through each track in the playlist
        for track in playlist['tracks']:
            # Extract the attributes
            attributes = {
                'playlist_name': playlist['name'],
                'track_name': track['track_name'],
                'artist_name': track['artist_name'],
                'track_uri': track['track_uri'],
                'artist_uri': track['artist_uri'],
                'album_uri': track['album_uri'],
                'duration_ms': track['duration_ms'],
                'album_name': track['album_name']
            }
            # Add the attributes to the list
            tracks_attributes.append(attributes)

    # Create a DataFrame from the list
    df = pd.DataFrame(tracks_attributes)

    return df

def concatenate_json_files(folder_path):
    dfs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            json_file = os.path.join(folder_path, filename)
            dfs.append(json_to_df(json_file))
    return pd.concat(dfs, ignore_index=True)

# Example usage:
folder_path = '<replace with path to json files>'
final_df = concatenate_json_files(folder_path)

