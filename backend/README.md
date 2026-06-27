# Auto Clipper Platform - Backend

This is the backend implementation for the completely local, AI-powered Auto Clipper Platform. It automatically analyzes long-form videos, finds the most viral/engaging moments using a local LLM, and crops those moments into ready-to-post 9:16 vertical shorts.

## Architecture & Tools

This platform runs 100% locally with no cloud dependencies, ensuring complete privacy.

*   **API & Core Logic:** FastAPI (Python)
*   **Video Downloading:** `yt-dlp`
*   **Audio Extraction & Video Manipulation:** `ffmpeg-python` (Wrapper for FFmpeg)
*   **Speech-to-Text & Timestamps:** `faster-whisper`
*   **AI Highlight Detection & Metadata:** Local LLM via `Ollama`
*   **Auto-Reframing (Face Tracking):** OpenCV (`cv2`)
*   **Database:** SQLite (via SQLAlchemy)

## System Requirements

Before running the backend, you must have the following system dependencies installed:

1.  **FFmpeg:** Required for audio extraction and video cropping.
    *   *Ubuntu/Debian:* `sudo apt install ffmpeg`
    *   *macOS:* `brew install ffmpeg`
    *   *Windows:* Download from official site and add to PATH.
2.  **Ollama:** Required for the local AI analysis.
    *   Install from [ollama.com](https://ollama.com)
    *   Once installed, pull a model. We recommend a fast, small model for this task: `ollama run gemma2:2b` or `ollama run llama3.2:3b`.

## Installation

1.  Create a virtual environment (optional but recommended)
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

## Key Endpoints

*   `POST /upload`: Upload a local `.mp4`, `.mov`, etc.
*   `POST /youtube`: Submit a YouTube URL to download and process.
*   `GET /videos`: List all uploaded/downloaded videos and their processing status.
*   `GET /clips/{video_id}`: Retrieve the metadata and file paths for the generated clips of a specific video.

## Notes on Face Tracking

The current face tracking uses OpenCV's basic Haar cascades for demonstration. For production use, it is highly recommended to upgrade the `detect_faces_and_track` function in `video_processor.py` to use a more robust Deep Neural Network (DNN) approach like YOLO or Google's MediaPipe for smoother and more accurate auto-reframing.
