import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import random
import math

OFFSET_LIMIT = 50
SCOPE = "user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative user-modify-playback-state"

def establish_auth():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri="http://localhost:5173",
                                                   scope=SCOPE))
    return sp

def get_total_saved_tracks(sp):
    saved_tracks = sp.current_user_saved_tracks(limit=1)
    return saved_tracks['total']

def get_total_playlist(sp, playlist_id):
    playlist_tracks = sp.playlist_tracks(playlist_id, limit=1)
    return playlist_tracks['total']

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

def get_saved_tracks(sp, num_tracks=OFFSET_LIMIT):
    total_saved = get_total_saved_tracks(sp)
    track_ids = []
    
    if total_saved <= num_tracks:
        # If total saved tracks are less than the number of tracks needed
        results = sp.current_user_saved_tracks(limit=num_tracks)
        track_ids = [track['track']['id'] for track in results['items'] if track['track']]
        return track_ids[:num_tracks]

    # Calculate a valid random offset
    max_offset = math.floor(total_saved / OFFSET_LIMIT) * OFFSET_LIMIT
    rand_offset = random.randint(0, max_offset - OFFSET_LIMIT)
    
    results = sp.current_user_saved_tracks(limit=OFFSET_LIMIT, offset=rand_offset)

    while results and len(track_ids) < num_tracks:
        track_ids.extend(track['track']['id'] for track in results['items'] if track['track'])
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    return track_ids[:num_tracks]

def get_playlist_tracks(sp, playlist_id, num_tracks=OFFSET_LIMIT, offset=0):
    total_tracks = get_total_playlist(sp, playlist_id)
    track_ids = []

    if total_tracks <= num_tracks:
        # Fetch all tracks if the total number of tracks is less than or equal to num_tracks
        results = sp.playlist_tracks(playlist_id, limit=num_tracks)
        track_ids = [track['track']['id'] for track in results['items'] if track['track']]
        return track_ids[:num_tracks]

    # Calculate a valid random offset if needed
    max_offset = math.floor(total_tracks / OFFSET_LIMIT) * OFFSET_LIMIT
    if offset == 0:
        # Randomize the offset if not provided
        offset = random.randint(0, max_offset - OFFSET_LIMIT)
    
    results = sp.playlist_tracks(playlist_id, limit=OFFSET_LIMIT, offset=offset)

    while results and len(track_ids) < num_tracks:
        track_ids.extend(track['track']['id'] for track in results['items'] if track['track'])
        if results['next']:
            results = sp.next(results)
        else:
            break

    return track_ids[:num_tracks]

def push_to_queue(sp, track_ids):
    for track in track_ids:
        sp.add_to_queue(track, device_id=None)

def shuffle_saved_songs(sp, num_tracks):
    track_ids = get_saved_tracks(sp, num_tracks)
    random.shuffle(track_ids)
    return track_ids

def shuffle_playlist(sp, playlist_id, num_tracks):
    shuffled_playlist = []
    num_batches = math.ceil(num_tracks / OFFSET_LIMIT)
    
    for batch in range(num_batches):
        offset = batch * OFFSET_LIMIT
        tracks_batch = get_playlist_tracks(sp, playlist_id, OFFSET_LIMIT, offset)
        shuffled_playlist.extend(tracks_batch)
    
    random.shuffle(shuffled_playlist)
    return shuffled_playlist

sp = establish_auth()

playlist_id = choose_playlist(sp)
num_songs = int(input("How many songs should be added to queue? "))

if playlist_id == 'saved_songs':
    shuffled_playlist = shuffle_saved_songs(sp, num_songs)
else:
    shuffled_playlist = shuffle_playlist(sp, playlist_id, num_songs)

push_to_queue(sp, shuffled_playlist)
print(f"{num_songs} songs added to queue.")
