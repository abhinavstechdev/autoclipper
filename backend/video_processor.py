import yt_dlp
import ffmpeg
import cv2
import os
import uuid

def download_youtube_video(url, output_path="downloads"):
    os.makedirs(output_path, exist_ok=True)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
        return filename

def extract_audio(video_path, output_path=None):
    if output_path is None:
         os.makedirs("downloads", exist_ok=True)
         output_path = f"downloads/audio_{uuid.uuid4().hex}.wav"

    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_path, acodec='pcm_s16le', ac=1, ar='16k')
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except ffmpeg.Error as e:
        print(f"Error extracting audio: {e.stderr.decode('utf8')}")
        return None

def detect_faces_and_track(video_path, start_time=0.0, end_time=None):
    # This is a simplified face tracking implementation for demonstration
    # In a production app, use stronger DNN tracking (e.g. MediaPipe or YOLO)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(video_path)

    # Seek to start time
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(start_time * fps))

    centers = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if end_time and current_time > end_time:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            # Simple approach: track the largest face
            largest_face = max(faces, key=lambda f: f[2]*f[3])
            x, y, w, h = largest_face
            center_x = x + w // 2
            centers.append(center_x)
        else:
            # If no face, append last known or center
            if centers:
                centers.append(centers[-1])
            else:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                centers.append(width // 2)

    cap.release()

    # Calculate average center for a static crop, or return tracking data for dynamic
    if centers:
        avg_center = sum(centers) // len(centers)
        return avg_center

    return None

def create_srt_file(clip_segments, output_path, start_time):
    """Creates a basic SRT file for burned-in captions, adjusting timestamps relative to clip start."""
    srt_content = ""
    for idx, seg in enumerate(clip_segments):
        # Adjust segment times to be relative to the clip's start time
        seg_start = max(0.0, float(seg['start']) - start_time)
        seg_end = max(0.0, float(seg['end']) - start_time)

        def format_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            msecs = int((seconds - int(seconds)) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{msecs:03d}"

        srt_content += f"{idx + 1}\n"
        srt_content += f"{format_time(seg_start)} --> {format_time(seg_end)}\n"
        srt_content += f"{seg['text'].strip()}\n\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    return output_path

def generate_clip(input_path, output_path, start_time, end_time, clip_segments=None, center_x=None):
    # This combines cutting, cropping, and captioning
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    target_width = int(height * 9 / 16)

    if center_x is None:
         center_x = detect_faces_and_track(input_path, start_time, end_time)
         if center_x is None:
             center_x = width // 2

    x_start = max(0, center_x - target_width // 2)
    x_start = min(x_start, width - target_width)

    srt_path = None
    if clip_segments:
        srt_path = output_path.replace(".mp4", ".srt")
        create_srt_file(clip_segments, srt_path, start_time)

    try:
        stream = ffmpeg.input(input_path, ss=start_time, t=end_time-start_time)
        v_stream = stream.video.filter('crop', target_width, height, x_start, 0)

        if srt_path:
             # Basic styling for burned-in captions
             # Note: For real Opus style, you'd use a more advanced subtitle renderer like ASS or custom drawing.
             v_stream = v_stream.filter('subtitles', srt_path, force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=20')

        a_stream = stream.audio

        (
            ffmpeg
            .output(v_stream, a_stream, output_path, vcodec='libx264', crf=23, preset='fast', acodec='aac')
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except ffmpeg.Error as e:
         print(f"Error generating clip: {e.stderr.decode('utf8')}")
         return None
