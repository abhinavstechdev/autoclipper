import os
import subprocess
import logging

logger = logging.getLogger(__name__)

CLIPS_DIR = "/app/data/clips"
os.makedirs(CLIPS_DIR, exist_ok=True)

def create_clip(video_path: str, start_time: float, end_time: float, clip_id: int) -> str:
    """
    Cuts the video, applies a basic 9:16 crop (center crop for now), and returns the new file path.
    """
    output_filename = f"clip_{clip_id}.mp4"
    output_path = os.path.join(CLIPS_DIR, output_filename)

    # Simple center crop for 9:16 aspect ratio (e.g., 1080x1920)
    # Using ffmpeg directly for performance

    # Calculate duration
    duration = end_time - start_time

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-i", video_path,
        "-t", str(duration),
        "-vf", "crop=ih*(9/16):ih", # Crop to 9:16 maintaining height
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "aac",
        output_path
    ]

    try:
        logger.info(f"Running FFmpeg for clip {clip_id}")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Successfully generated clip {clip_id} at {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr.decode()}")
        raise
