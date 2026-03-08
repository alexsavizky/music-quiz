import random


class MusicQuiz:
    def __init__(self, spotify_service):
        self.api = spotify_service
        self.total_rounds = 5

    def generate_full_quiz(self):
        """Generates a list of 5 distinct questions in one API call."""
        quiz_package = []

        # We grab 5 different artists from your top list to ensure variety
        for i in range(1, self.total_rounds + 1):
            try:
                # Use ranks 1-5 for a "Top Hits" feel
                artist = self.api.get_artist_by_rank(i)
                question_data = self.name_that_tune_by_artist(artist, True)
                quiz_package.append(question_data)
            except Exception as e:
                print(f"Error generating round {i}: {e}")

        return quiz_package

    def name_that_tune_by_artist(self, artist, start_at_random=False):
        tracks = self.api.get_tracks_via_search(artist["name"])

        # Filter for tracks that actually have a URI
        valid_tracks = [t for t in tracks if t.get("uri")]
        correct_track = random.choice(valid_tracks)

        other_names = list(
            set([t["name"] for t in tracks if t["name"] != correct_track["name"]])
        )
        decoys = random.sample(other_names, 3)

        options = decoys + [correct_track["name"]]
        random.shuffle(options)
        if start_at_random:
            duration = int(correct_track["duration_ms"])
            random_start = random.randint(10000, int(duration * 0.6))
        else:
            random_start = 0
        return {
            "artist_name": artist["name"],
            "question": f"Name this {artist['name']} song:",
            "correct_name": correct_track["name"],
            "track_uri": correct_track["uri"],
            "options": options,
            "start_at_ms": random_start,
        }
