import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

scope = "user-top-read user-read-playback-state user-modify-playback-state streaming user-read-email user-read-private"


class SpotifyService:
    def __init__(self, cache_handler, scope=scope):
        load_dotenv()
        self.auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            cache_handler=cache_handler,
            scope=scope,
            show_dialog=True,
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_artist_by_rank(self, rank: int):
        """Fetches the artist at a specific position (1-50) in user's top list."""
        # Offset is rank - 1 because API is 0-indexed
        results = self.sp.current_user_top_artists(
            limit=1, offset=rank - 1, time_range="medium_term"
        )

        if not results["items"]:
            return None

        artist = results["items"][0]
        return {"id": artist["id"], "name": artist["name"]}

    def get_tracks_via_search(self, artist_name: str):
        query = f"artist:{artist_name}"
        results = self.sp.search(q=query, type="track", limit=10)

        # We no longer look for 'preview_url'
        return [
            {
                "name": t["name"],
                "album": t["album"]["name"],
                "duration_ms": t["duration_ms"],
                "release_date": t["album"]["release_date"],
                "uri": t["uri"],
            }
            for t in results["tracks"]["items"]
        ]

    def play_song(sp, track_uri):
        # This tells your ACTIVE Spotify device to start playing this track
        sp.start_playback(uris=[track_uri])
        print("Song started on your Spotify device!")

    def artist_albums(self, artist_id, album_type="album", limit=10):
        # This calls the actual spotipy client (self.sp)
        return self.sp.artist_albums(artist_id, album_type=album_type, limit=limit)

    def album_tracks(self, album_id):
        # This calls the actual spotipy client to get songs from a specific album
        return self.sp.album_tracks(album_id)

    def get_artist_id_by_name(self, name):
        # Search for the artist
        results = self.sp.search(q=f"artist:{name}", type="artist", limit=1)
        items = results.get("artists", {}).get("items", [])

        if not items:
            return None

        # Return the ID of the first (most relevant) result
        return items[0]["id"]
