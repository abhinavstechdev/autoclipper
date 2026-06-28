import os
import json
from faster_whisper import WhisperModel
import logging
import time

logger = logging.getLogger(__name__)

TRANSCRIPTS_DIR = "/app/data/transcripts"
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

# Determine device
try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
except ImportError:
    device = "cpu"
    compute_type = "int8"

logger.info(f"Loading Whisper model on {device}...")
model = WhisperModel("base", device=device, compute_type=compute_type)
logger.info("Whisper model loaded.")

def transcribe_video(video_path: str, video_id: int) -> dict:
    """
    Transcribes a video using faster-whisper and returns word-level timestamps.
    """
    start_time = time.time()
    logger.info(f"Starting transcription for {video_path}")

    # We use word_timestamps=True as requested
    segments, info = model.transcribe(video_path, word_timestamps=True)

    transcript_data = {
        "language": info.language,
        "language_probability": info.language_probability,
        "segments": []
    }

    full_text = ""
    for segment in segments:
        segment_dict = {
            "id": segment.id,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
            "words": [{"word": w.word, "start": w.start, "end": w.end, "probability": w.probability} for w in segment.words] if segment.words else []
        }
        transcript_data["segments"].append(segment_dict)
        full_text += segment.text + " "

    transcript_data["full_text"] = full_text.strip()

    # Save to file
    output_path = os.path.join(TRANSCRIPTS_DIR, f"{video_id}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Transcription complete in {time.time() - start_time:.2f}s")
    return transcript_data
