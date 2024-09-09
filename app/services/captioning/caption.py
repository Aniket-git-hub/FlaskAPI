import os
import subprocess
import assemblyai as aai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

# Set your OpenAI API key
aai.settings.api_key = ""
FFMPEG_PATH = 'ffmpeg'

import os
import subprocess
import assemblyai as aai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

FFMPEG_PATH = 'ffmpeg'

def get_captions_srt(video_path):
    """
    Convert video to audio, transcribe it using AssemblyAI, and save as SRT.
    
    Args:
    video_path (str): Path to the input video file.
    
    Returns:
    str: Path to the generated SRT file.
    
    Raises:
    Exception: If any error occurs during the process.
    """
    try:
        # Extract audio for transcription
        transcription_audio = video2mp3(video_path, output_prefix="transcription_")
        
        # Transcribe the audio
        transcript = transcribe_audio_openai(transcription_audio)
        
        # Save transcript to SRT file
        srt_path = os.path.splitext(video_path)[0] + '.srt'
        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            srt_file.write(transcript)
        
        return srt_path
    except Exception as e:
        raise Exception(f"Error in get_captions_srt: {str(e)}")

def video2mp3(video_path, output_ext="mp3", output_prefix="transcription_"):
    """
    Convert video to mp3 using ffmpeg.
    
    Args:
    video_path (str): Path to the input video file.
    output_ext (str): Desired output audio format (default is "mp3").
    output_prefix (str): Prefix for the output audio file.
    
    Returns:
    str: Path to the output audio file.
    
    Raises:
    Exception: If video conversion fails.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    filename, _ = os.path.splitext(video_path)
    output_audio_path = f"{output_prefix}{os.path.basename(filename)}.{output_ext}"
    
    try:
        subprocess.run(
            [FFMPEG_PATH, "-y", "-i", video_path, output_audio_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        return output_audio_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error converting video to audio: {str(e)}")
    except Exception as e:
        raise Exception(f"Error in video2mp3: {str(e)}")

def transcribe_audio_openai(audio_file):
    """
    Transcribes audio using AssemblyAI API.
    
    Args:
    audio_file (str): Path to the audio file.
    
    Returns:
    str: The transcription in SRT format.
    
    Raises:
    Exception: If transcription fails.
    """
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    transcriber = aai.Transcriber()
    try:
        with open(audio_file, "rb") as file:
            transcript = transcriber.transcribe(file)
        return transcript.export_subtitles_srt()  
    except Exception as e:
        raise Exception(f"Error in generating transcript srt: {str(e)}")


def burn_captions(video_path, srt_path, font_size=24, font_color='white', font_name='Arial', 
                  background_color=None, margin=(10, 10), animation=None):
    """
    Burns the SRT captions onto the video using MoviePy with customizable options.
    Reattaches the original audio after burning captions.
    
    Args:
    video_path (str): Path to the input video file.
    srt_path (str): Path to the SRT file.
    font_size (int): Font size for the captions (default is 24).
    font_color (str): Font color for the captions (default is 'white').
    font_name (str): Font name for the captions (default is 'Arial').
    background_color (str or None): Background color for the captions (default is None for transparency).
    margin (tuple): Margin around the captions in pixels (default is (10, 10)).
    animation (function or None): Optional animation function for the captions (default is None).

    Returns:
    str: Path to the output video with burned captions and original audio.

    Raises:
    Exception: If caption burning or audio reattaching fails.
    """
    try:
        # Load the video and extract audio
        video = VideoFileClip(video_path)
        audio = video.audio

        # Create a helper function to create TextClip with custom properties
        def create_text_clip(text, start, end):
            txt_clip = TextClip(text, fontsize=font_size, font=font_name, color=font_color, bg_color=background_color)
            txt_clip = txt_clip.set_duration(end - start).set_start(start)
            txt_clip = txt_clip.margin(left=margin[0], right=margin[1], top=0, bottom=0)
            if animation:
                txt_clip = animation(txt_clip)
            return txt_clip

        # Read the SRT file and create TextClips for each subtitle
        subtitles = []
        with open(srt_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        # Parse the SRT file content
        for line in content:
            if line.strip() == '':
                continue
            if '-->' in line:
                start, end = line.split(' --> ')
                start = time_to_seconds(start)
                end = time_to_seconds(end)
            elif not line.strip().isdigit():
                text = line.strip()
                subtitles.append(create_text_clip(text, start, end))

        # Combine subtitles with the video (without audio)
        final_video = CompositeVideoClip([video] + subtitles, size=video.size)

        # Define output path for the captioned video (without audio)
        processed_folder = os.path.join(os.getcwd(), 'processed_videos')
        os.makedirs(processed_folder, exist_ok=True)
        original_filename = os.path.basename(video_path)
        processed_filename = f"captioned_{original_filename}"
        processed_clip_path = os.path.join(processed_folder, processed_filename)

        # Write the captioned video without audio
        temp_video_path = os.path.join(processed_folder, f"temp_{original_filename}")
        final_video.write_videofile(temp_video_path, codec='libx264', audio=False)

        # Reattach the original audio using FFmpeg
        reattached_audio_path = reattach_audio(temp_video_path, video_path)
        
        return reattached_audio_path
    except Exception as e:
        raise Exception(f"Error in burn_captions: {str(e)}")

def time_to_seconds(time_str):
    """
    Converts SRT time format to seconds.
    
    Args:
    time_str (str): Time in SRT format (e.g., '00:01:23,456').
    
    Returns:
    float: Time in seconds.
    """
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def reattach_audio(video_with_captions, original_video_path):
    """
    Reattach the original audio from the original video to the video with captions.
    
    Args:
    video_with_captions (str): Path to the video with captions but no audio.
    original_video_path (str): Path to the original video with audio.
    
    Returns:
    str: Path to the final video with audio and captions.
    """
    try:
        # Extract audio from the original video
        original_audio_file = video2mp3(original_video_path, output_ext="aac", output_prefix="original_audio_")

        # Use ffmpeg to combine video with the extracted audio
        output_path = os.path.splitext(video_with_captions)[0] + '_with_audio.mp4'
        command = f"{FFMPEG_PATH} -y -i {video_with_captions} -i {original_audio_file} -c:v copy -c:a aac {output_path}"
        subprocess.run(command, shell=True, check=True)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error in reattaching audio: {str(e)}")


# Example usage:
# Define an animation function (e.g., a fade-in effect)
def fade_in(txt_clip):
    return txt_clip.crossfadein(1)

