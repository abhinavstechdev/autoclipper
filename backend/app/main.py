from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models import Video, Clip
from app.services.downloader import download_youtube_video
from app.services.transcriber import transcribe_video
from app.services.ai_highlighter import detect_highlights
from app.services.video_editor import create_clip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auto Clipper Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlUploadRequest(BaseModel):
    url: str

def process_video_pipeline(video_id: int, url: str, db: Session):
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return

        video.status = "downloading"
        db.commit()

        # 1. Download
        video_path = download_youtube_video(url)

        video.status = "transcribing"
        db.commit()

        # 2. Transcribe
        transcript_data = transcribe_video(video_path, video_id)

        video.status = "analyzing"
        db.commit()

        # 3. Analyze for highlights
        highlights = detect_highlights(transcript_data)

        # 4. Generate clips
        for hl in highlights:
            clip = Clip(
                video_id=video.id,
                start_time=hl.get("start_time", 0.0),
                end_time=hl.get("end_time", 0.0),
                title=hl.get("title", "Generated Clip"),
                virality_score=hl.get("virality_score", 0),
                status="reframing"
            )
            db.add(clip)
            db.commit()
            db.refresh(clip)

            try:
                clip_path = create_clip(video_path, clip.start_time, clip.end_time, clip.id)
                clip.filepath = clip_path
                clip.status = "completed"
            except Exception as e:
                logger.error(f"Failed to cut clip: {e}")
                clip.status = "failed"

            db.commit()

        video.status = "completed"
        db.commit()

    except Exception as e:
        logger.error(f"Pipeline error for video {video_id}: {e}")
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = "failed"
            db.commit()


@app.get("/")
def read_root():
    return {"message": "Auto Clipper Platform API is running"}

@app.post("/api/videos/url")
def upload_youtube_url(request: UrlUploadRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    video = Video(original_url=request.url, status="pending")
    db.add(video)
    db.commit()
    db.refresh(video)

    background_tasks.add_task(process_video_pipeline, video.id, request.url, db)

    return {"message": "Video accepted for processing", "video_id": video.id}

@app.get("/api/videos")
def list_videos(db: Session = Depends(get_db)):
    return db.query(Video).all()

@app.get("/api/clips")
def list_clips(db: Session = Depends(get_db)):
    # Need to return duration derived from start and end time
    clips = db.query(Clip).order_by(Clip.created_at.desc()).all()
    result = []
    for c in clips:
        result.append({
            "id": c.id,
            "video_id": c.video_id,
            "title": c.title,
            "duration": c.end_time - c.start_time if c.end_time and c.start_time else 0,
            "virality_score": c.virality_score,
            "status": c.status
        })
    return result
