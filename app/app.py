import os
import random
from flask import Flask, session, url_for, redirect, render_template, request, jsonify
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from dotenv import load_dotenv
from spotify.spotify_service import SpotifyService
from game.game_maneger import MusicQuiz

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)  # Required for sessions


cache_handler = FlaskSessionCacheHandler(session)


sp = SpotifyService(cache_handler)
mq = MusicQuiz(sp)


# --- ROUTES ---
@app.route("/")
def index():
    """Main Menu: Shows profile and quiz selection."""
    if not sp.auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = sp.auth_manager.get_authorize_url()
        return redirect(auth_url)

    # Fetch User Profile Info
    user_info = sp.sp.current_user()
    user_name = user_info.get("display_name", "Music Explorer")

    # Get profile image if it exists, else use a placeholder
    images = user_info.get("images", [])
    user_img = images[0]["url"] if images else "https://via.placeholder.com/150"

    return render_template("index.html", user_name=user_name, user_img=user_img)


@app.route("/callback")
def callback():
    """Spotify redirects here after user logs in."""
    sp.auth_manager.get_access_token(request.args.get("code"))
    return redirect(url_for("index"))


@app.route("/game")
def game_page():
    """Initial page load. Just provides the frame and the token."""
    token_info = cache_handler.get_cached_token()
    return render_template("game.html", token=token_info["access_token"])


@app.route("/api/get-quiz-package")
def get_quiz_package():
    # Read params from the JS fetch call
    limit = int(request.args.get("limit", 5))
    difficulty = request.args.get("diff", "mid")
    mode = request.args.get("mode", "collection")
    artist_name = request.args.get("artist", None)
    artist_id = request.args.get("artist_id", None)
    try:
        pool_size = int(request.args.get("pool_size", 0))
    except (ValueError, TypeError):
        pool_size = 0

    # Generate the package using your MusicQuiz class
    # You will need to update your MusicQuiz methods to handle these variables!
    package = mq.generate_name_that_tune_quiz(
        limit=limit,
        difficulty=difficulty,
        mode=mode,
        artist_name=artist_name,
        pool_size=pool_size,
        artist_id=artist_id,
    )

    return jsonify({"rounds": package})


@app.route("/play/<device_id>/<track_uri>/<int:start_ms>")
def play(device_id, track_uri, start_ms):
    # The 'position_ms' argument tells Spotify where to jump
    sp.sp.start_playback(device_id=device_id, uris=[track_uri], position_ms=start_ms)
    return jsonify({"status": "success"})


@app.route("/transfer/<device_id>")
def transfer_playback(device_id):
    # This officially moves the "Active" status to your browser
    # play=True ensures it starts immediately if something was already playing
    sp.sp.transfer_playback(device_id=device_id, force_play=True)
    return jsonify({"status": "transferred"})


@app.route("/profile")
def profile():
    if not sp.auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(url_for("index"))

    user_info = sp.sp.current_user()

    # We'll pass dummy stats for now since we haven't built the database yet
    stats = {
        "games_played": 12,
        "win_rate": "75%",
        "avg_score": "4.2/5",
        "top_genre": "Pop",
    }

    return render_template("profile.html", user=user_info, stats=stats)


@app.route("/lobby/<game_type>")
def lobby(game_type):
    token_info = cache_handler.get_cached_token()
    if not token_info:
        return redirect(url_for("index"))

    # Define metadata for the lobby based on game type
    game_titles = {
        "name_that_tune": "Name That Tune",
        "artist_guesser": "Who's the Artist?",
        "album_master": "Album Art Challenge",
    }

    title = game_titles.get(game_type, "New Challenge")

    return render_template("lobby.html", game_type=game_type, title=title)


@app.route("/logout")
def logout():
    # Clear the session/cache to sign out
    import os

    if os.path.exists(".cache"):
        os.remove(".cache")
    return redirect(url_for("index"))


@app.route("/api/search-artist")
def search_artist():
    query = request.args.get("q", "")
    if not query or len(query) < 2:
        return jsonify([])

    # Search for artists only
    results = sp.sp.search(q=f"artist:{query}", type="artist", limit=5)
    artists = results.get("artists", {}).get("items", [])

    suggestions = []
    for a in artists:
        suggestions.append(
            {
                "id": a["id"],
                "name": a["name"],
                "image": (
                    a["images"][-1]["url"]
                    if a["images"]
                    else "https://via.placeholder.com/50"
                ),
            }
        )

    return jsonify(suggestions)


def get_cached_top_artists(self):
    # Check if we already have the artists in the user's session
    if "top_artists" in session:
        print("📊 Using Cached Artists")
        return session["top_artists"]

    # If not, fetch them ONCE
    print("🌍 Calling Spotify API: /v1/me/top/artists")
    results = self.sp.current_user_top_artists(limit=50, time_range="medium_term")
    artists = results.get("items", [])

    # Store just the necessary info in the session to keep it light
    simplified_artists = [{"id": a["id"], "name": a["name"]} for a in artists]

    session["top_artists"] = simplified_artists
    return simplified_artists


if __name__ == "__main__":
    app.run(debug=True, port=8000)
