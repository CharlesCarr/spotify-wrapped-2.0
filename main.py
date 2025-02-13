from database.db_manager import init_db, get_db
from spotify.spotify_client import SpotifyClient
from models.track import Track
from models.listen import Listen
import logging
from datetime import datetime
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup():
    init_db()


def get_latest_listen_timestamp(db):
    result = db.query(Listen.played_at).order_by(Listen.played_at.desc()).first()
    return result[0] if result else None


def main():
    setup()
    spotify_client = SpotifyClient()

    try:
        db = next(get_db())

        # Get the timestamp of our most recent listen
        latest_timestamp = get_latest_listen_timestamp(db)

        # Get recent tracks from Spotify
        recent_tracks = spotify_client.get_recent_tracks()

        tracks_added = 0
        listens_added = 0

        for track_data, played_at in recent_tracks:
            # Skip if we already have this listen
            if latest_timestamp and played_at <= latest_timestamp:
                logger.info(
                    f"Skipping already recorded listen: {track_data.name} at {played_at}"
                )
                continue

            # Check if track exists, if not add it
            existing_track = (
                db.query(Track).filter_by(spotify_id=track_data.spotify_id).first()
            )
            if not existing_track:
                db.add(track_data)
                tracks_added += 1
                db.flush()  # Flush to get the track ID

            # Create new listen
            listen = Listen(track_id=track_data.spotify_id, played_at=played_at)
            db.add(listen)
            listens_added += 1

        db.commit()
        logger.info(
            f"Added {tracks_added} new tracks and {listens_added} new listens to database"
        )

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
