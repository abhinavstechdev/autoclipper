from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import shutil
import os
import json

from backend.database import SessionLocal, init_db, get_db, Video, Clip
from backend.video_processor import download_youtube_video, extract_audio, generate_clip
from backend.transcriber import transcribe_audio
from backend.highlight_detector import detect_highlights, match_highlights_to_timestamps

app = FastAPI(title="Auto Clipper Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("clips", exist_ok=True)

class YouTubeRequest(BaseModel):
    url: str

def process_video_pipeline(video_id: int, file_path: str):
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return

        video.status = "processing_audio"
        db.commit()

        # 1. Extract Audio
        audio_path = extract_audio(file_path)
        if not audio_path:
            raise Exception("Failed to extract audio")

        video.status = "transcribing"
        db.commit()

        # 2. Transcribe
        transcript_path, transcript_text = transcribe_audio(audio_path)
        if not transcript_path:
            raise Exception("Failed to transcribe audio")

        video.transcript_path = transcript_path
        db.commit()

        video.status = "analyzing_highlights"
        db.commit()

        # 3. Detect Highlights using Ollama
        with open(transcript_path, 'r') as f:
            transcript_data = json.load(f)

        raw_highlights = detect_highlights(transcript_text)

        if not raw_highlights:
            # Fallback if LLM fails: create a dummy clip from the first 30 seconds
            print("Warning: LLM returned no highlights. Generating fallback clip.")
            clip_data = [{
                "title": "Fallback Highlight",
                "start_time": 0.0,
                "end_time": min(30.0, float(transcript_data['segments'][-1]['end']) if transcript_data['segments'] else 30.0),
                "virality_score": 50.0,
                "hook_strength": 50.0,
                "retention_prediction": 50.0,
                "engagement_prediction": 50.0,
                "sentiment_analysis": "Neutral",
                "topic_category": "General"
            }]
        else:
            clip_data = match_highlights_to_timestamps(raw_highlights, transcript_data['segments'])

        video.status = "generating_clips"
        db.commit()

        # 4. Generate actual video clips
        for idx, clip_info in enumerate(clip_data):
            output_clip_path = f"clips/video_{video_id}_clip_{idx}.mp4"

            # Find relevant transcript segments for this clip
            clip_segments = [
                seg for seg in transcript_data['segments']
                if seg['start'] < clip_info['end_time'] and seg['end'] > clip_info['start_time']
            ]

            # This also handles vertical reframing and captions
            res_path = generate_clip(
                file_path,
                output_clip_path,
                clip_info['start_time'],
                clip_info['end_time'],
                clip_segments=clip_segments
            )

            if res_path:
                db_clip = Clip(
                    video_id=video_id,
                    title=clip_info['title'],
                    start_time=clip_info['start_time'],
                    end_time=clip_info['end_time'],
                    virality_score=clip_info['virality_score'],
                    hook_strength=clip_info['hook_strength'],
                    retention_prediction=clip_info['retention_prediction'],
                    engagement_prediction=clip_info['engagement_prediction'],
                    sentiment_analysis=clip_info['sentiment_analysis'],
                    topic_category=clip_info['topic_category'],
                    filepath=output_clip_path
                )
                db.add(db_clip)

        video.status = "completed"
        db.commit()

    except Exception as e:
        print(f"Pipeline error: {e}")
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = "failed"
            db.commit()
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_video = Video(filename=file.filename, status="pending")
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    background_tasks.add_task(process_video_pipeline, new_video.id, file_location)

    return {"message": "Video uploaded successfully and processing started", "video_id": new_video.id}

@app.post("/youtube")
async def process_youtube(req: YouTubeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Create DB entry first
    new_video = Video(source_url=req.url, filename=f"youtube_{hash(req.url)}", status="downloading")
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    def download_and_process():
        # Open an inner session for db commit since outside is closed
        inner_db = SessionLocal()
        try:
            file_path = download_youtube_video(req.url)
            # Update filename once downloaded
            v = inner_db.query(Video).filter(Video.id == new_video.id).first()
            if v:
                 v.filename = os.path.basename(file_path)
                 inner_db.commit()
            inner_db.close()
            process_video_pipeline(new_video.id, file_path)
        except Exception as e:
            print(f"Error downloading YouTube video: {e}")
            v = inner_db.query(Video).filter(Video.id == new_video.id).first()
            if v:
                v.status = "failed"
                inner_db.commit()
            inner_db.close()

    background_tasks.add_task(download_and_process)

    return {"message": "YouTube download queued", "video_id": new_video.id}

@app.get("/videos")
def get_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).all()
    return videos

@app.get("/clips/{video_id}")
def get_clips_for_video(video_id: int, db: Session = Depends(get_db)):
    clips = db.query(Clip).filter(Clip.video_id == video_id).all()
    if not clips:
        raise HTTPException(status_code=404, detail="No clips found for this video")
    return clips
