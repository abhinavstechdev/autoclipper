import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

def detect_highlights(transcript_text, model="gemma2:2b"):
    # Using a smaller model by default for speed if running locally without strong GPU

    prompt = f"""
    You are an expert short-form video editor specializing in viral content for TikTok, YouTube Shorts, and Instagram Reels.
    Analyze the following video transcript and identify the top 3 most engaging, viral, or interesting moments.

    For each moment, provide:
    1. A catchy title.
    2. The exact text quote that starts the clip.
    3. The exact text quote that ends the clip.
    4. A virality score from 1-100.
    5. A hook strength score from 1-100.
    6. A retention prediction from 1-100.
    7. An engagement prediction from 1-100.
    8. The primary sentiment (e.g., Funny, Educational, Controversial, Motivational).
    9. A topic category.

    Return the response ONLY as a valid JSON array of objects. Do not include any markdown formatting like ```json.

    Transcript:
    {transcript_text}
    """

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()

        result_text = response.json().get('response', '')

        # Try to parse the response as JSON directly
        try:
            highlights = json.loads(result_text)
            # Ensure it's a list
            if isinstance(highlights, dict) and "clips" in highlights:
                highlights = highlights["clips"]
            elif isinstance(highlights, dict) and "highlights" in highlights:
                highlights = highlights["highlights"]

            if not isinstance(highlights, list):
                # wrap in list if it returned a single object
                highlights = [highlights]

            return highlights

        except json.JSONDecodeError:
            print("Failed to parse Ollama response as JSON. Response was:")
            print(result_text)
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return []

def match_highlights_to_timestamps(highlights, transcript_segments):
    """
    Matches the start and end text quotes from Ollama to the actual timestamps
    in the transcript data.
    """
    processed_clips = []

    for highlight in highlights:
        start_quote = highlight.get('start_quote', '')
        end_quote = highlight.get('end_quote', '')

        if not start_quote or not end_quote:
            continue

        # Simplified matching logic: find the segment containing the start quote
        start_time = 0.0
        end_time = 0.0

        start_found = False

        # Simple word-based matching for robustness against minor LLM variations
        start_words = start_quote.lower().split()
        if not start_words:
            continue

        first_word = start_words[0]

        for segment in transcript_segments:
            if not start_found:
                if first_word in segment['text'].lower():
                     start_time = segment['start']
                     start_found = True

            if start_found:
                 # Check if the end quote is in this segment
                 end_words = end_quote.lower().split()
                 if end_words:
                     last_word = end_words[-1]
                     if last_word in segment['text'].lower():
                         end_time = segment['end']
                         break

        if start_found and end_time > start_time:
            # Enforce constraints (15s to 90s)
            duration = end_time - start_time
            if duration < 15.0:
                # Pad to 15s if possible
                end_time = start_time + 15.0
            elif duration > 90.0:
                # Trim to 90s max
                end_time = start_time + 90.0

            clip_data = {
                "title": highlight.get('title', 'Generated Clip'),
                "start_time": start_time,
                "end_time": end_time,
                "virality_score": float(highlight.get('virality_score', 75)),
                "hook_strength": float(highlight.get('hook_strength', 70)),
                "retention_prediction": float(highlight.get('retention_prediction', 70)),
                "engagement_prediction": float(highlight.get('engagement_prediction', 70)),
                "sentiment_analysis": highlight.get('sentiment', 'Neutral'),
                "topic_category": highlight.get('topic_category', 'General')
            }
            processed_clips.append(clip_data)

    return processed_clips
