from faster_whisper import WhisperModel
import json
import os

# Set compute_type="int8" to reduce memory usage on CPU
# Use device="cuda" if running on a machine with a GPU
def transcribe_audio(audio_path, model_size="base", device="cpu", compute_type="int8"):
    try:
        print(f"Loading Whisper model '{model_size}' on {device}...")
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        print(f"Transcribing {audio_path}...")
        # word_timestamps=True allows us to pinpoint exactly when things are said
        segments, info = model.transcribe(audio_path, beam_size=5, word_timestamps=True)

        transcript_data = []
        full_text = ""

        for segment in segments:
            segment_dict = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "words": [{"word": word.word, "start": word.start, "end": word.end} for word in segment.words]
            }
            transcript_data.append(segment_dict)
            full_text += segment.text + " "

        print(f"Transcription complete. Detected language: {info.language} with probability {info.language_probability}")

        # Save transcript to file
        output_file = audio_path.replace(".wav", "_transcript.json")
        with open(output_file, 'w') as f:
            json.dump({"text": full_text.strip(), "segments": transcript_data}, f, indent=4)

        return output_file, full_text.strip()

    except Exception as e:
        print(f"Error during transcription: {e}")
        return None, None
