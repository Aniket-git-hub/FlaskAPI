import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips

def merge_clips(video_path, clips_info):
    """
    Function to merge video clips based on timestamps and save the merged clip in the processed folder.
    The number of clips is limited to 10.
    """
    try:
        # Ensure no more than 10 clips are processed
        if len(clips_info) > 10:
            return {"error": "Cannot merge more than 10 clips"}

        # Load the video file
        video = VideoFileClip(video_path)
        clips = []

        # Processed folder path
        processed_folder = os.path.join(os.getcwd(), 'processed_videos')  # You can pass from Flask's config
        os.makedirs(processed_folder, exist_ok=True)

        # Iterate over clip_info and create subclips
        for idx, clip_info in enumerate(clips_info):
            start_time = convert_time_to_seconds(clip_info['start'])
            end_time = convert_time_to_seconds(clip_info['end'])

            # Extract the clip and add to the list
            clip = video.subclip(start_time, end_time)
            clips.append(clip)

        # Merge the clips
        merged_clip = concatenate_videoclips(clips)

        # Save the merged clip
        original_filename = os.path.basename(video_path)
        processed_filename = f"processed_merge_{original_filename}"
        processed_clip_path = os.path.join(processed_folder, processed_filename)
        merged_clip.write_videofile(processed_clip_path, codec="libx264")

        return processed_clip_path

    except Exception as e:
        raise Exception(f"Error merging video: {e}")

def convert_time_to_seconds(time_str):
    """Converts a HH:MM:SS string to seconds."""
    if isinstance(time_str, str) and ':' in time_str:
        h, m, s = [int(i) for i in time_str.split(':')]
        return h * 3600 + m * 60 + s
    return time_str  # If already in seconds
