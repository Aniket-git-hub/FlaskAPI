from moviepy.video.io.VideoFileClip import VideoFileClip
import os
from flask import current_app

def create_clips(video_path, clips_info):
    """
    Function to create video clips from a video file.

    Parameters:
        video_path (str): The path to the original video file.
        clips_info (list): A list of dictionaries, each containing 'start' and 'end' times in seconds or HH:MM:SS format.
    
    Returns:
        List of paths of the generated clips.
    """
    try:
        # Processed folder path
        processed_folder = os.path.join(os.getcwd(), 'processed_videos')  # You can pass from Flask's config
        os.makedirs(processed_folder, exist_ok=True)
        
        # Load the video file
        video = VideoFileClip(video_path)
        clips = []
        clip_paths = []

        # Create clips based on provided timestamps
        for idx, clip_info in enumerate(clips_info):
            start_time = clip_info['start']
            end_time = clip_info['end']
            
            # Convert time format if in HH:MM:SS
            start_time = convert_time_to_seconds(start_time)
            end_time = convert_time_to_seconds(end_time)

            # Extract the clip from the original video
            clip = video.subclip(start_time, end_time)
            original_filename = os.path.basename(video_path)
            processed_filename = f"clip_{idx + 1}_{original_filename}.mp4"
            processed_clip_path = os.path.join(processed_folder, processed_filename)
            clip.write_videofile(processed_clip_path, codec="libx264")
            clip_paths.append(processed_clip_path)

        return clip_paths

    except Exception as e:
        # Raise the exception to be handled by the parent function
        raise Exception(f"Error processing video clips: {e}")

def convert_time_to_seconds(time_str):
    """
    Convert a time string in the format HH:MM:SS to seconds.
    """
    if isinstance(time_str, str) and ':' in time_str:
        h, m, s = [int(i) for i in time_str.split(':')]
        return h * 3600 + m * 60 + s
    return time_str  # If already in seconds
