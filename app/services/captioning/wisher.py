# app/services/captioning/whisper.py

import whisper

def generate_captions_whisper(video_path):
    model = whisper.load_model("small")
    result = model.transcribe(video_path)

    # Check if any text is generated
    if not result.get('text'):
        return None

    # Generate the SRT file
    srt_path = video_path.replace(".mp4", ".srt")
    with open(srt_path, 'w') as srt_file:
        for i, segment in enumerate(result['segments']):
            start = segment['start']
            end = segment['end']
            text = segment['text']

            srt_file.write(f"{i+1}\n")
            srt_file.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            srt_file.write(f"{text}\n\n")

    return srt_path

def format_timestamp(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = seconds * 1000 % 1000
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"
