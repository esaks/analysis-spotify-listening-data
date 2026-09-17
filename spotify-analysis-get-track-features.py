# import modules
import requests
import pandas as pd
import json
import time
import os

# import listening history with track ids
listeningdata=pd.read_csv('Spotifyanalysisfolder/listening_history_with_ids.csv')

# Create manual cache
cache_file = os.path.join(
    os.path.dirname(__file__),
    "listeningdata_lookup.json")
if os.path.exists(cache_file): 
    with open(cache_file, "r") as f:
        listeningdata_lookup = json.load(f) #if it exists, call it lookup_table
else:
    listeningdata_lookup = {} # otherwise, create an empty lookup table for now

# Just query the unique tracks
unique_tracks = listeningdata.dropna(subset=["track_id"]).drop_duplicates(subset=["artistName", "trackName"])

# Query
for index, row in unique_tracks.iterrows():
    #endTime = row["endTime"]
    artist_name = row["artistName"]
    track_name = row["trackName"]
    #msplayed = row["msPlayed"]
    track_id = row["track_id"]
    cache_key = f"{artist_name}|||{track_name}" #create cache_key for this unique artist and song combo
    
    # Set URL
    url = "https://api.reccobeats.com/v1/audio-features"

    if cache_key in listeningdata_lookup: # if that song/artist combo ID has already been found, append the ID and move onto the next song/artist
        print(f"Cache Hit: {track_name} by {artist_name}")
        continue 

    else:
        # Run query
        params = {"ids": track_id}
        result = requests.get(url, params=params)
        #print(result.json())
        time.sleep(.5)

        if result.status_code == 200:
            data = result.json()
            print(data)
   
            if not data.get("content"): # if content is empty return empty list
                print(f"No features found for {track_name}")
                continue

            else:
                track_features = data["content"][0]
                items = {
                    "tempo": track_features.get("tempo"),
                    "energy": track_features.get("energy"),
                    "danceability": track_features.get("danceability"), 
                    "valence": track_features.get("valence"),    
                    "acousticness": track_features.get("acousticness"),
                    "instrumentalness": track_features.get("instrumentalness"),
                    "liveness": track_features.get("liveness"),
                    "loudness": track_features.get("loudness"),
                    "speechiness": track_features.get("speechiness")
                }
                if items:
                    listeningdata_lookup[cache_key] = items
                    print(f"Cached {track_name} by {artist_name}")

        elif result.status_code == 429: # Need to handle 429 error
            # Save progress so far to the cache file
            with open(cache_file, "w") as f: #create or open the cache file
                json.dump(listeningdata_lookup, f) #save lookup table into the cache file
            # Wait
            wait_time = result.headers.get("Retry-After")
            print(f"Hit rate limit. Waiting {wait_time} seconds...")
            time.sleep(int(wait_time))
            

        else: #other error
            print(result.status_code)
            print(result.url)
            print(result.text)
            break

# Do a final save if it reaches the end
with open(cache_file, "w") as f: #create or open the cache file
    json.dump(listeningdata_lookup, f) #save lookup talble into the cache file

# Convert lookup table to df
listeningdata_list = []
for key, features in listeningdata_lookup.items():
    if features and "|||" in key:
        artist, track= key.split("|||")
        row_dict = {"artistName": artist, "trackName": track} # new role with artist and track
        row_dict.update(features) # add third item features with all features saved inside
        listeningdata_list.append(row_dict) #append to list

listening_data_df = pd.DataFrame(listeningdata_list)

# merge features back into full listening history with ids and features
final_listening_data = listeningdata.merge(
    listening_data_df,
    on=["artistName", "trackName"], 
    how="left"
)

# Save as csv
output_path = 'Spotifyanalysisfolder'
final_listening_data.to_csv("Spotifyanalysisfolder/final_listening_data.csv", index=False)

