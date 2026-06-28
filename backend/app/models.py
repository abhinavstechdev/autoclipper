from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_url = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, downloading, transcribing, analyzing, completed, failed
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    clips = relationship("Clip", back_populates="video", cascade="all, delete-orphan")

class Clip(Base):
    __tablename__ = "clips"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    start_time = Column(Float)
    end_time = Column(Float)
    title = Column(String)
    virality_score = Column(Float, nullable=True)
    status = Column(String, default="pending") # pending, reframing, completed, failed
    filepath = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="clips")
