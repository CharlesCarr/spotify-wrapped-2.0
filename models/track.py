from sqlalchemy import Column, Integer, String, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from database.db_manager import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, index=True, unique=True)
    name = Column(String)
    artist = Column(String)
    artist_id = Column(String)
    genres = Column(JSON)
    album = Column(String)
    album_id = Column(String)
    duration_ms = Column(Integer)
    popularity = Column(Integer)

    tempo = Column(Float, nullable=True)
    energy = Column(Float, nullable=True)
    danceability = Column(Float, nullable=True)
    valence = Column(Float, nullable=True)
    acousticness = Column(Float, nullable=True)
    instrumentalness = Column(Float, nullable=True)
    key = Column(Integer, nullable=True)
    mode = Column(Integer, nullable=True)
    time_signature = Column(Integer, nullable=True)

    is_explicit = Column(Boolean, default=False)
    preview_url = Column(String, nullable=True)
    external_urls = Column(JSON)

    listens = relationship("Listen", back_populates="track")

    def __repr__(self):
        return f"<Track {self.name} by {self.artist}>"
