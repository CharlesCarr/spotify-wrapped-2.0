from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db_manager import Base
from datetime import datetime


class Listen(Base):
    __tablename__ = "listens"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(String, ForeignKey("tracks.spotify_id"))
    played_at = Column(DateTime, index=True)

    # Relationship to Track
    track = relationship("Track", back_populates="listens")

    def __repr__(self):
        return f"<Listen of {self.track_id} at {self.played_at}>"
