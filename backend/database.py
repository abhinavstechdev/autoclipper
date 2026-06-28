from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./autoclipper.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    source_url = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, processing, completed, failed
    duration = Column(Float, nullable=True)
    transcript_path = Column(String, nullable=True)

    clips = relationship("Clip", back_populates="video")


class Clip(Base):
    __tablename__ = "clips"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    title = Column(String)
    start_time = Column(Float)
    end_time = Column(Float)
    virality_score = Column(Float)
    hook_strength = Column(Float)
    retention_prediction = Column(Float)
    engagement_prediction = Column(Float)
    sentiment_analysis = Column(String)
    topic_category = Column(String)
    filepath = Column(String, nullable=True)

    video = relationship("Video", back_populates="clips")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
