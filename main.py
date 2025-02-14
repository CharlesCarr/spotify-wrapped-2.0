from database.db_manager import init_db, get_db
from spotify.spotify_client import SpotifyClient
from models.track import Track
from models.listen import Listen
import logging
from datetime import datetime, timezone
from sqlalchemy import select


def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("logs/spotify_tracker.log"),
            logging.StreamHandler(),  # This will also print to console
        ],
    )
    return logging.getLogger(__name__)


def setup():
    init_db()


def get_latest_listen_timestamp(db):
    result = db.query(Listen.played_at).order_by(Listen.played_at.desc()).first()
    if result and result[0]:
        if result[0].tzinfo is None:
            return result[0].replace(tzinfo=timezone.utc)
        return result[0]
    return None


def main():
    logger = setup_logging()
    logger.info("Starting Spotify tracking script")

    setup()
    spotify_client = SpotifyClient()

    try:
        db = next(get_db())
        logger.info("Database connection established")

        # Get the timestamp of our most recent listen
        latest_timestamp = get_latest_listen_timestamp(db)
        logger.info(f"Latest timestamp from database: {latest_timestamp}")

        # Get recent tracks from Spotify
        recent_tracks = spotify_client.get_recent_tracks()
        logger.info(f"Retrieved {len(recent_tracks)} tracks from Spotify")

        tracks_added = 0
        listens_added = 0

        for track_data, played_at in recent_tracks:
            # Ensure played_at has timezone info if it doesn't already
            if played_at.tzinfo is None:
                played_at = played_at.replace(tzinfo=timezone.utc)

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

            logger.debug(f"Processing track: {track_data.name} played at {played_at}")

        db.commit()
        logger.info(
            f"Session complete: Added {tracks_added} new tracks and {listens_added} new listens to database"
        )

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    main()
