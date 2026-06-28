import json
import logging
import requests
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

def detect_highlights(transcript_data: dict, model_name: str = "qwen:0.5b") -> List[Dict[str, Any]]:
    """
    Uses local Ollama to find highlights in the transcript.
    """
    full_text = transcript_data.get("full_text", "")

    if not full_text:
        return []

    prompt = f"""
    Analyze the following transcript from a video. Identify the most engaging, viral, funny, or educational moments.
    For each moment, extract the EXACT text spoken. Do not alter the text.
    Return a JSON array of objects, where each object has:
    - 'quote': The exact text of the moment (between 15 and 90 seconds worth of speaking).
    - 'reasoning': Why this moment is good.
    - 'virality_score': A score from 1 to 100 predicting how viral it could be.
    - 'title': A catchy, viral title for this clip.

    Transcript:
    "{full_text}"

    Output ONLY valid JSON. No markdown, no introductory text.
    """

    logger.info(f"Sending request to Ollama with model {model_name}...")
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=180
        )
        response.raise_for_status()
        result = response.json()

        response_text = result.get("response", "[]").strip()

        try:
            highlights = json.loads(response_text)
            if not isinstance(highlights, list):
                highlights = [highlights]
            return _match_highlights_to_timestamps(highlights, transcript_data)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Ollama output as JSON: {response_text}")
            return []

    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return []

def _match_highlights_to_timestamps(highlights: List[Dict], transcript_data: dict) -> List[Dict]:
    """
    Tries to map the plain text quotes back to actual start and end timestamps in the video.
    """
    segments = transcript_data.get("segments", [])
    valid_clips = []

    for hl in highlights:
        quote = hl.get("quote", "").strip()
        if not quote:
            continue

        # Very simple fuzzy matching: find the first segment that contains a significant chunk of the quote
        # In a real app, you'd use a more robust sequence alignment algorithm

        start_time = None
        end_time = None

        # Naive approach: find segment where it starts, and where it ends
        quote_words = quote.lower().split()
        if not quote_words:
            continue

        first_word = quote_words[0]
        last_word = quote_words[-1]

        for i, segment in enumerate(segments):
            seg_text = segment["text"].lower()
            if first_word in seg_text and start_time is None:
                start_time = segment["start"]

            if last_word in seg_text and start_time is not None:
                end_time = segment["end"]
                break

        # Fallback if not found perfectly
        if start_time is None:
            continue

        if end_time is None or end_time <= start_time:
            # Just take a 30s chunk or until end of next few segments
            end_time = start_time + 30.0

        hl["start_time"] = start_time
        hl["end_time"] = end_time
        valid_clips.append(hl)

    return valid_clips
