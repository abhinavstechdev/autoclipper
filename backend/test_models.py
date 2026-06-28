import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Video, Clip

DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def db_session():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_video(db_session):
    video = Video(original_url="http://test.com", status="pending")
    db_session.add(video)
    db_session.commit()
    assert video.id is not None
    assert video.status == "pending"

def test_create_clip(db_session):
    video = db_session.query(Video).first()
    clip = Clip(video_id=video.id, start_time=10.0, end_time=20.0, title="Funny Moment")
    db_session.add(clip)
    db_session.commit()
    assert clip.id is not None
    assert clip.title == "Funny Moment"
    assert clip.video_id == video.id
