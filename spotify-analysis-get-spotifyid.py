# Import modules
import requests
import pandas as pd
import base64
import json
import time
import os
import dotenv import load_dotenv

# Read in listening history from spotify as data frames
listening_history1 = pd.read_csv('data/StreamingHistory_music_0.csv')
listening_history2 = pd.read_csv('data/StreamingHistory_music_1.csv')

# merge listening histories
listening_history = pd.concat([listening_history1, listening_history2], ignore_index=True)

# Create manual cache store
cache_file = os.path.join(
    os.path.dirname(__file__),
    "listeninghistory_lookup_table.json")
if os.path.exists(cache_file): 
    with open(cache_file, "r") as f:
        lookup_table = json.load(f) #if it exists, call it lookup_table
else:
    lookup_table = {} # otherwise, create an empty lookup table for now

# Authorization for Spotify API
load_dotenv()
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
# Request token access by senting client id, client secret and grant type to spotify accounts service.
def get_token():
    author_string = client_id + ":" + client_secret
    auth_bytes = author_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"  # authorization query url

    headers = {'Authorization': "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    result= requests.post(url, headers=headers, data=data) # will return JSON data in a field called content
    if result.status_code == 200:
        result_content = json.loads(result.content) #convert json to dictionary
        token =result_content["access_token"]
        return token
    else:
        print(result.status_code)
        print(result.text)

# only run once
token = get_token()

# Use Spotify API to get track ids for songs in listening history
#token=
def get_track_ids(token, streaming_history): #takes in the access token and the streaminghistory csv file from spotify
    track_ids=[]
    for index, row in streaming_history.iterrows():
        artist_name = row["artistName"]
        track_name = row["trackName"]
        cache_key = f"{artist_name}|||{track_name}" #create cache_key for this unique artist and song combo

        if cache_key in lookup_table: # if that song/artist combo ID has already been found, append the ID and move onto the next song/artist
            print(f"Cache Hit: {track_name} by {artist_name}")
            track_ids.append(lookup_table[cache_key])
            continue 
        
        # If not in cache:
        params = { # to get something like ?q={artist_name}&type=artist&limit=1&{track_name}&type=track&limit=1
            "q": f'track:"{track_name}" artist:"{artist_name}"',
            "type": "track",
            "limit": 1,
            "market": "US"
        }
        url = "https://api.spotify.com/v1/search"
        header_for_calls = {"Authorization": "Bearer " + token}

        result = requests.get(url, headers=header_for_calls, params=params)
        time.sleep(.5)

        try:
            data = result.json()
            items = data["tracks"]["items"]
            if items:
                found_id = items[0]["id"]
                lookup_table[cache_key] = found_id # update lookup table only if id found
            else:
                # Try broader search with just track and artist name as a plain search string, may get more hits for song titles with special characters
                print(f"Running looser search for {track_name} by {artist_name}")
                params["q"] = f'{track_name} {artist_name}'  # Just the song and artist names together
                result = requests.get(url, headers=header_for_calls, params=params)
                data = result.json()
                items = data.get("tracks", {}).get("items", [])
                if items:
                    found_id = items[0]["id"]
                    lookup_table[cache_key] = found_id
                else:
                    found_id = None # Otherwise, conclude we were unable to findn the id
            
            track_ids.append(found_id) # append the id to the list
            

        except:
            if result.status_code == 429: # Need to handle 429 error

                # Save progress so far to the cache file
                with open(cache_file, "w") as f: #create or open the cache file
                    json.dump(lookup_table, f) #save lookup table into the cache file
                
                # Wait
                wait_time = result.headers.get("Retry-After")
                print(f"Hit rate limit. Waiting {wait_time} seconds...")
                time.sleep(int(wait_time))
            else: #other error
                print(result.status_code)
                print(result.url)
                print(result.text)

    # Do a final save if it reaches the end
    with open(cache_file, "w") as f: #create or open the cache file
        json.dump(lookup_table, f) #save lookup talble into the cache file

    return track_ids

# get track ids for only the unique songs to limit api requests
unique_tracks = listening_history.drop_duplicates(subset=["artistName", "trackName"])
ids = get_track_ids(token, unique_tracks)
print(f"Total unique IDs fetched: {len(ids)}")

# convert lookup table to df
lookup_df = []
for key, track_id in lookup_table.items():
    if track_id:
        artist, track= key.split("|||")
        lookup_df.append({
            "artistName": artist,
            "trackName": track,
            "track_id": track_id
        })

lookup_df = pd.DataFrame(lookup_df)

# merge ids to listening history
listening_history_with_ids = listening_history.merge(
    lookup_df,
    on=["artistName", "trackName"], 
    how="left"
)

# Save as csv
output_path = 'Spotifyanalysisfolder'
listening_history_with_ids.to_csv("Spotifyanalysisfolder/listening_history_with_ids.csv", index=False)

