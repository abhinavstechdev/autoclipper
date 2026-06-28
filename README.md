# Auto Clipper Platform

A fully local, privacy-focused alternative to Opus Clip that automatically converts long-form videos into viral short-form reels.

## Overview

Users can upload long video files or provide YouTube URLs. The system automatically processes the video entirely locally, using:
- **FastAPI / Python Backend:** For managing jobs, processing video, and handling logic.
- **Next.js / React Frontend:** A dark-themed (Lumina Core style) web dashboard to view and manage clips.
- **Faster-Whisper:** For high-accuracy local speech-to-text with word-level timestamps.
- **Ollama (Local LLMs):** For intelligent highlight detection, generating titles, and calculating virality scores.
- **FFmpeg & OpenCV:** For automated reframing (9:16 vertical crop).
- **SQLite:** For fast, local storage without cloud dependencies.

## Prerequisites

Before running the application, ensure you have the following installed on your system:
- **Node.js** (v18+ recommended) and npm
- **Python** (v3.10+ recommended)
- **FFmpeg** (Must be installed and available in your system's PATH)
- **Ollama** (Must be installed and running locally on port 11434 with models pulled)

## Setup Instructions

### 1. Database and Storage Configuration

The system uses a `./data` directory in the root of the project to store SQLite databases, downloaded videos, transcripts, and generated clips.

```bash
mkdir -p data/videos data/transcripts data/clips
```

### 2. Backend Setup

The backend is built with FastAPI. It handles video downloading, transcription, LLM interactions, and FFmpeg processing.

```bash
# Navigate to the backend directory
cd backend

# Install Python dependencies (consider using a virtual environment)
pip install -r requirements.txt

# Run database migrations to initialize the SQLite database
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```
The API will be available at `http://localhost:8000`.

### 3. Frontend Setup

The frontend is a Next.js App Router application styled with Tailwind CSS.

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Next.js development server
npm run dev &
```
The frontend application will be available at `http://localhost:3000`.

## How to Use

1. Ensure both the FastAPI backend (`http://localhost:8000`) and the Next.js frontend (`http://localhost:3000`) are running.
2. Ensure Ollama is running locally (`http://localhost:11434`).
3. Open your browser and go to `http://localhost:3000`.
4. Click **Upload Video** from the dashboard.
5. Paste a YouTube URL and click **Import**. The video will download and process in the background.
6. Navigate to **My Clips** to see the generated reels, their lengths, and their AI-determined Virality Score.

## Project Structure

- `frontend/` - Next.js React frontend (Tailwind CSS, App Router)
- `backend/` - FastAPI Python backend
  - `app/main.py` - Core API endpoints and background task manager
  - `app/services/downloader.py` - `yt-dlp` integration
  - `app/services/transcriber.py` - `faster-whisper` integration
  - `app/services/ai_highlighter.py` - Local LLM integration via Ollama
  - `app/services/video_editor.py` - FFmpeg integration for vertical cropping
- `data/` - (Created at runtime) Local storage for DB and media files
