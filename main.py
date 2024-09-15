import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import random

SCOPE = "user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative user-modify-playback-state"

# returns a spotipy 'sp' instance after auth
def establish_auth():
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= client_id,
                                                client_secret= client_secret,
                                                redirect_uri="http://localhost:5173",
                                                scope=SCOPE))
    return sp

# returns total tracks in liked songs playlist
def get_total_saved_tracks(sp):
    saved_tracks = sp.current_user_saved_tracks(limit=1)
    return saved_tracks['total']

# returns total tracks of a playlist
def get_total_playlist(sp, playlist_id):
    playlist_tracks = sp.playlist_tracks(playlist_id,limit=1)
    return playlist_tracks['total']

# returns id of playlist or 'saved_songs' if saved songs selected.
def choose_playlist(sp):
    selected_playlist = None
    playlist_ids = []
    user_playlists = sp.current_user_playlists(limit=50)
    
    print("1. Saved Songs")
    for idx, item in enumerate(user_playlists['items']):
        print(f"{idx + 2}: {item['name']}")
        playlist_ids.append(item['id'])

    choice = int(input("Enter number of playlist to shuffle: "))
    if choice == 1:
        return 'saved_songs'
    if choice > 1:
        selected_playlist = playlist_ids[choice - 2]

    return selected_playlist

# returns list of track ids
def get_saved_tracks(sp, num_tracks=50,offset=0):
     tracks = sp.current_user_saved_tracks(limit=num_tracks, offset=offset)
     track_ids = [track['track']['id'] for track in tracks['items'] if track['track']]
     return track_ids

# returns list of track ids
def get_playlist_tracks(sp, playlist_id, num_tracks=50, offset=0):
        tracks = sp.playlist_tracks(playlist_id, limit=num_tracks, offset=offset)
        track_ids = [track['track']['id'] for track in tracks['items'] if track['track']]
        return track_ids

def push_to_queue(sp, track_ids):
     for track in track_ids:
          sp.add_to_queue(track,device_id=None)






sp = establish_auth()

playlist_id = choose_playlist(sp)

if playlist_id == 'saved_songs':
     track_ids = get_saved_tracks(sp)
else:
    track_ids = get_playlist_tracks(sp,playlist_id)

random.shuffle(track_ids)
push_to_queue(sp, track_ids)
