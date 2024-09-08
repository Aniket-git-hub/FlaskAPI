from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import os

def add_logo_to_video(video_path, logo_path, position):
    """
    Add a logo to the video throughout its duration.
    
    Parameters:
    - video_path: Path to the video file.
    - logo_path: Path to the logo image file.
    - position: Tuple or string specifying the position of the logo. For example: ('right', 'bottom'), ('center', 'top')
    """
    try:
        video_path = os.path.join(os.getcwd(), video_path.lstrip('/'))
        logo_path = os.path.join(os.getcwd(), logo_path.lstrip('/'))
        
        video = VideoFileClip(video_path)
        logo = ImageClip(logo_path).set_duration(video.duration).resize(height=50)  # Resize logo to fit

        # Set the logo position
        if isinstance(position, str):
            position = position.lower()
            if position == 'top_left':
                position = ('left', 'top')
            elif position == 'top_right':
                position = ('right', 'top')
            elif position == 'bottom_left':
                position = ('left', 'bottom')
            elif position == 'bottom_right':
                position = ('right', 'bottom')
            elif position == 'center':
                position = ('center', 'center')
            else:
                position = ('right', 'bottom')  # Default position if unknown
        
        logo = logo.set_position(position).margin(right=30, bottom=30, top=30, left=30)

        # Overlay the logo on the video
        final_video = CompositeVideoClip([video, logo])

        # Define the output path in the processed folder
        processed_folder = os.path.join(os.getcwd(), 'processed_videos')
        os.makedirs(processed_folder, exist_ok=True)
        output_filename = f"processed_logo_{os.path.basename(video_path)}"
        output_path = os.path.join(processed_folder, output_filename)

        # Save the output video
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        if os.path.exists(logo_path):
            os.remove(logo_path)
            
        return output_path

    except Exception as e:
        raise Exception(f"Error adding logo to video: {e}")
