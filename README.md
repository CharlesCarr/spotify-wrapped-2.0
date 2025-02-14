# Spotify Listening History Tracker

A Python application that tracks your Spotify listening history and stores it in a local SQLite database for analysis. The app captures detailed track information, including audio features, genres, and each time you listen to a track.

## Features

- Tracks every song you listen to on Spotify
- Stores rich metadata including:
  - Basic track information (name, artist, album)
  - Audio features (tempo, energy, danceability)
  - Genre information
  - Listening timestamps
- Supports multiple plays of the same track
- Local SQLite database storage

## Prerequisites

- Python 3.x
- Spotify account
- Spotify Developer account with registered application

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd spotify-tracker
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your Spotify credentials:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   ```

## Setup

1. Create a Spotify Developer Application:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Add `http://localhost:8888/callback` to the Redirect URIs
   - Copy the Client ID and Client Secret to your `.env` file

2. Initialize the database:
   ```bash
   python main.py
   ```

## Usage

Run the application manually:
```bash
python main.py
```

The first run will:
1. Open your browser for Spotify authentication
2. Create a local database
3. Fetch your recent listening history

For regular tracking, run the application periodically (e.g., every few hours).

### macOS Scheduling

To run automatically on macOS:

Using crontab:
```bash
# Open crontab editor
crontab -e

# Add this line to run every 6 hours
0 */6 * * * cd /path/to/project && /usr/bin/python3 main.py >> /tmp/spotify_tracker.log 2>&1
```

## Automated Scheduling (macOS)

To set up automatic tracking every 3 hours:

1. Ensure your `.env` file includes your script path:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   SCRIPT_PATH=/path/to/your/spotify-wrapped-2.0/main.py
   ```

2. Run the setup script:
   ```bash
   python3 setup_scheduler.py
   ```

This will configure the script to run:
- When you log in to your Mac
- Every 3 hours from 9 AM to 9 PM (at 9 AM, 12 PM, 3 PM, 6 PM, and 9 PM)

### Managing the Scheduler

To verify the scheduler is running:
```bash
launchctl list | grep com.yourapp.scheduler
```

To manually trigger the script:
```bash
launchctl start com.yourapp.scheduler
```

To remove the scheduler:
```bash
launchctl unload ~/Library/LaunchAgents/com.yourapp.scheduler.plist
rm ~/Library/LaunchAgents/com.yourapp.scheduler.plist
```

### Logging

The application uses a comprehensive logging system that tracks:
- Script execution times
- Track processing details
- Spotify API interactions
- Any errors or warnings

Log files are stored in the `logs` directory:
- `logs/spotify_scheduler.log`: Contains general execution logs
- `logs/spotify_scheduler.error.log`: Contains error logs

To view logs in real-time:
```bash
tail -f logs/spotify_scheduler.log
```

## Database Structure

The application uses two main tables:

1. `tracks`: Stores unique track information
   - Basic details (name, artist, album)
   - Audio features (tempo, energy, etc.)
   - Genre information

2. `listens`: Records each time you play a track
   - Track reference
   - Timestamp

## Analysis Possibilities

The data structure allows for various analyses:
- Most played tracks
- Listening patterns by time of day
- Genre preferences over time
- Audio feature trends
- Custom queries for specific insights

Example queries:
```python
# Get top 10 most played tracks
def get_top_tracks(db, limit=10):
    return db.query(
        Track,
        func.count(Listen.id).label('play_count')
    ).join(Listen).group_by(Track.spotify_id)\
    .order_by(desc('play_count')).limit(limit).all()

# Get listening patterns by hour
def get_hourly_patterns(db):
    return db.query(
        func.strftime('%H', Listen.played_at).label('hour'),
        func.count(Listen.id)
    ).group_by('hour').order_by('hour').all()
```

## File Structure

```
spotify_tracker/
│
├── config/
│   └── config.py          # Configuration settings
│
├── database/
│   ├── __init__.py
│   └── db_manager.py      # Database connection management
│
├── models/
│   ├── __init__.py
│   ├── track.py          # Track model definition
│   └── listen.py         # Listen model definition
│
├── spotify/
│   ├── __init__.py
│   └── spotify_client.py  # Spotify API integration
│
├── logs/                 # Log directory
│   ├── spotify_scheduler.log
│   └── spotify_scheduler.error.log
│
├── main.py               # Main application entry point
├── setup_scheduler.py    # Scheduler setup script
├── com.yourapp.scheduler.plist  # LaunchD configuration
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables (not in git)
└── README.md            # This file
```

## Troubleshooting

1. **Authentication Issues**:
   - Ensure your Spotify credentials are correct in `.env`
   - Check that your redirect URI matches exactly in both `.env` and Spotify Dashboard

2. **Database Issues**:
   - If database errors occur, try deleting the `spotify_history.db` file and rerunning
   - Ensure you have write permissions in the project directory

3. **Scheduler Issues**:
   - Verify the scheduler is running with `launchctl list | grep com.yourapp.scheduler`
   - Check logs in `logs/spotify_scheduler.log` for errors
   - Ensure SCRIPT_PATH in `.env` points to the correct location
   - Try manually triggering the script with `launchctl start com.yourapp.scheduler`

4. **Log Issues**:
   - Ensure the `logs` directory exists and is writable
   - Check both `.log` files for different types of errors
   - Use `tail -f logs/spotify_scheduler.log` to watch logs in real-time

## Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Spotipy](https://spotipy.readthedocs.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)