import yt_dlp
import os
import uuid

VIDEO_DIR = "/app/data/videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

def download_youtube_video(url: str) -> str:
    """
    Downloads a youtube video to local storage using yt-dlp.
    Returns the path to the downloaded file.
    """
    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(VIDEO_DIR, filename)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_path

def save_uploaded_file(file_content: bytes, extension: str) -> str:
    """
    Saves an uploaded file to local storage.
    """
    filename = f"{uuid.uuid4()}.{extension}"
    output_path = os.path.join(VIDEO_DIR, filename)

    with open(output_path, "wb") as f:
        f.write(file_content)

    return output_path
