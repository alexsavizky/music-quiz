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
    """Home page: check if logged in, otherwise redirect to login."""
    if not sp.auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = sp.auth_manager.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for("game"))


@app.route("/callback")
def callback():
    """Spotify redirects here after user logs in."""
    sp.auth_manager.get_access_token(request.args.get("code"))
    return redirect(url_for("game_page"))


@app.route("/game")
def game_page():
    """Initial page load. Just provides the frame and the token."""
    token_info = cache_handler.get_cached_token()
    return render_template("game.html", token=token_info["access_token"])


@app.route("/api/get-quiz-package")
def get_quiz_package():
    """The single endpoint that delivers all 5 rounds at once."""
    # Generate the 5 questions
    package = mq.generate_full_quiz()

    # We return this as JSON for the JS to store in memory
    return jsonify(
        {"rounds": package, "total_rounds": len(package), "initial_lives": 2}
    )


@app.route("/api/next")
def next_round():
    mq.current_round += 1
    if mq.is_game_over():
        return jsonify({"game_over": True, "win": mq.lives > 0, "score": mq.score})

    res = mq.get_next_question()
    return jsonify(
        {
            "game_over": False,
            "question": res["question"],
            "correct_name": res["correct_name"],
            "track_uri": res["track_uri"],
            "options": res["options"],
            "round": mq.current_round,
            "lives": mq.lives,
        }
    )


@app.route("/play/<device_id>/<track_uri>")
def play(device_id, track_uri):
    """API endpoint called by JS to trigger the music."""
    try:
        sp.sp.start_playback(device_id=device_id, uris=[track_uri])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/transfer/<device_id>")
def transfer_playback(device_id):
    # This officially moves the "Active" status to your browser
    # play=True ensures it starts immediately if something was already playing
    sp.sp.transfer_playback(device_id=device_id, force_play=True)
    return jsonify({"status": "transferred"})


if __name__ == "__main__":
    app.run(debug=True, port=8000)
