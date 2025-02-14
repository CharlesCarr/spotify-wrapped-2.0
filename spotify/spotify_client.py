import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
from datetime import datetime, timezone
from models.track import Track
import logging


class SpotifyClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=" ".join(
                    [
                        "user-read-recently-played",
                        "user-read-currently-playing",
                        "user-read-playback-state",
                        "user-top-read",
                        "user-read-private",
                        "user-library-read",
                        "playlist-read-private",
                        "playlist-read-collaborative",
                        "streaming",
                    ]
                ),
            )
        )
        self.logger.info("SpotifyClient initialized successfully")

    def get_recent_tracks(self, limit=50):
        self.logger.info(f"Fetching {limit} recent tracks")
        results = self.sp.current_user_recently_played(limit=limit)
        tracks_with_timestamps = []

        for item in results["items"]:
            track = item["track"]
            played_at = datetime.strptime(
                item["played_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).replace(tzinfo=timezone.utc)

            try:
                # Get artist information
                artist = self.sp.artist(track["artists"][0]["id"])

                # Try to get audio features, but don't fail if we can't
                try:
                    audio_features = self.sp.audio_features([track["id"]])[0] or {}
                except Exception as e:
                    self.logger.warning(
                        f"Could not get audio features for {track['name']}: {str(e)}"
                    )
                    audio_features = {}

                track_data = Track(
                    spotify_id=track["id"],
                    name=track["name"],
                    artist=track["artists"][0]["name"],
                    artist_id=track["artists"][0]["id"],
                    genres=artist["genres"],
                    album=track["album"]["name"],
                    album_id=track["album"]["id"],
                    duration_ms=track["duration_ms"],
                    popularity=track["popularity"],
                    # Audio features are now optional
                    tempo=audio_features.get("tempo"),
                    energy=audio_features.get("energy"),
                    danceability=audio_features.get("danceability"),
                    valence=audio_features.get("valence"),
                    acousticness=audio_features.get("acousticness"),
                    instrumentalness=audio_features.get("instrumentalness"),
                    key=audio_features.get("key"),
                    mode=audio_features.get("mode"),
                    time_signature=audio_features.get("time_signature"),
                    is_explicit=track["explicit"],
                    preview_url=track.get("preview_url"),
                    external_urls=track["external_urls"],
                )

                tracks_with_timestamps.append((track_data, played_at))
                self.logger.info(f"Successfully processed track: {track['name']}")

            except Exception as e:
                self.logger.error(f"Error processing track {track['name']}: {str(e)}")
                continue

        return tracks_with_timestamps
