from moviepy.editor import VideoFileClip
from PIL import Image
from flask import current_app
import os

def change_aspect_ratio(video_path, aspect_ratio):
    """
    Function to change the aspect ratio of the video and save the processed video in the processed folder.
    """
    try:
        # Load the video file
        video = VideoFileClip(video_path)
        
        # Determine the target aspect ratio
        if aspect_ratio == "16:9":
            target_width, target_height = 16, 9
        elif aspect_ratio == "9:16":
            target_width, target_height = 9, 16
        elif aspect_ratio == "1:1":
            target_width, target_height = 1, 1
        elif aspect_ratio == "4:3":
            target_width, target_height = 4, 3
        else:
            raise ValueError(f"Invalid aspect ratio: {aspect_ratio}")

        # Calculate new dimensions
        original_width, original_height = video.size
        target_aspect_ratio = target_width / target_height
        original_aspect_ratio = original_width / original_height

        if original_aspect_ratio > target_aspect_ratio:
            # Video is wider than target aspect ratio; crop sides
            new_width = int(target_height * original_aspect_ratio)
            new_height = original_height
        else:
            # Video is taller than target aspect ratio; crop top and bottom
            new_width = original_width
            new_height = int(target_width / original_aspect_ratio)

        # Create the resized video
        resized_video = video.resize(newsize=(new_width, new_height))

        # Center crop to target aspect ratio
        x_center = new_width // 2
        y_center = new_height // 2
        crop_x1 = x_center - (target_width // 2)
        crop_y1 = y_center - (target_height // 2)
        crop_x2 = crop_x1 + target_width
        crop_y2 = crop_y1 + target_height

        cropped_video = resized_video.crop(x1=crop_x1, y1=crop_y1, x2=crop_x2, y2=crop_y2)

        # Processed folder path
        processed_folder = os.path.join(os.getcwd(), 'processed')  # You can pass from Flask's config
        os.makedirs(processed_folder, exist_ok=True)

        # Save the processed video
        original_filename = os.path.basename(video_path)
        processed_filename = f"processed_aspect_ratio_{aspect_ratio}_{original_filename}"
        processed_clip_path = os.path.join(processed_folder, processed_filename)
        cropped_video.write_videofile(processed_clip_path, codec="libx264")

        return {"processed_clip_path": processed_clip_path}

    except Exception as e:
        print(f"Error changing aspect ratio: {e}")
        return {"error": str(e)}
