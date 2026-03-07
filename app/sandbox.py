import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from spotify.spotify_service import SpotifyService

load_dotenv()

scope = "user-modify-playback-state user-read-playback-state"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=scope,
    )
)

spotify_service = SpotifyService(sp)
print(f"Logged in as: {sp.me()['display_name']}")
# id = spotify_service.get_artist_by_rank(1)["id"]
# print(spotify_service.get_playable_tracks_for_artist(id))
# test_id = "1dfeR4v9oUqy3933bnvYzp"
# print(spotify_service.get_playable_tracks_for_artist(test_id))
results = spotify_service.get_tracks_via_search("queen")
print(results)
