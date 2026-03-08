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

    def generate_name_that_tune_quiz(
        self,
        limit=5,
        difficulty="mid",
        mode="collection",
        artist_name=None,
        pool_size=0,
    ):
        """Generates a quiz package based on the specified parameters."""
        quiz_package = []

        # For simplicity, we'll just use the top artists for now
        for i in range(1, limit + 1):
            try:
                if artist_name:
                    id = self.api.get_artist_id_by_name(artist_name)

                    question_data = self.name_that_tune_by_artist(
                        {"name": artist_name, "id": id}, True, True
                    )
                else:
                    artist = self.api.get_artist_by_rank(
                        random.randint(1, pool_size + 1)
                    )
                    question_data = self.name_that_tune_by_artist(artist, True, False)
                quiz_package.append(question_data)
            except Exception as e:
                print(f"Error generating round {i}: {e}")

        return quiz_package

    def name_that_tune_by_artist(
        self, artist, start_at_random=False, from_albums=False
    ):
        # --- 1. Get Tracks Pool ---
        if from_albums:
            # Get artist's albums (limit to 5 to keep it fast/diverse)
            # Using artist['id'] is much more accurate than search
            album_results = self.api.artist_albums(
                artist["id"], album_type="album", limit=5
            )
            tracks_pool = []
            for album in album_results["items"]:
                album_tracks = self.api.album_tracks(album["id"])["items"]
                tracks_pool.extend(album_tracks)
        else:
            # Your original search-based logic
            tracks_pool = self.api.get_tracks_via_search(artist["name"])

        # --- 2. Filter & Pick Correct Track ---
        valid_tracks = [t for t in tracks_pool if t.get("uri")]

        # Safety check in case an artist has no albums/tracks
        if not valid_tracks:
            return None

        correct_track = random.choice(valid_tracks)

        # --- 3. Create Decoys ---
        # We pull decoys from the same pool to ensure they are the same artist
        other_names = list(
            set([t["name"] for t in tracks_pool if t["name"] != correct_track["name"]])
        )

        # Safety check for sample size
        sample_size = min(len(other_names), 3)
        decoys = random.sample(other_names, sample_size)

        # --- 4. Final Formatting ---
        options = decoys + [correct_track["name"]]
        random.shuffle(options)

        if start_at_random:
            # Note: album_tracks sometimes misses duration_ms in simplified objects,
            # so we use .get() with a fallback
            duration = int(correct_track.get("duration_ms", 180000))
            random_start = (
                random.randint(10000, int(duration * 0.6)) if duration > 20000 else 0
            )
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
