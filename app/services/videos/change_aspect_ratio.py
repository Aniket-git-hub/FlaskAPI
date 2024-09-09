import cv2
import numpy as np
import os
from moviepy.editor import VideoFileClip

def detect_face(frame):
    """
    Detect the face in the frame using OpenCV's Haar Cascade classifier.
    """
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) > 0:
        # Return the first detected face
        return faces[0]
    return None

def change_aspect_ratio(video_path, aspect_ratio, output_path=None):
    """
    Function to change the aspect ratio of the video while keeping the face centered,
    and save the processed video in the processed folder.

    Args:
    video_path (str): Path to the input video file.
    aspect_ratio (str): Desired aspect ratio (e.g., "16:9", "9:16", "1:1", "4:3").
    output_path (str, optional): Path to the output video file. If not provided, it will be saved in the 'processed_videos' folder.

    Returns:
    str: Path to the processed video file.
    """
    try:
        # Open the video with OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Unable to open video file")

        # Get video properties
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        original_codec = int(cap.get(cv2.CAP_PROP_FOURCC))
        original_codec_name = ''.join(chr(int(c)) for c in [original_codec & 0xFF, (original_codec >> 8) & 0xFF, (original_codec >> 16) & 0xFF, (original_codec >> 24) & 0xFF])

        # Determine the target dimensions
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

        target_aspect_ratio = target_width / target_height
        original_aspect_ratio = original_width / original_height

        # Calculate new dimensions
        if original_aspect_ratio > target_aspect_ratio:
            new_width = int(target_height * original_aspect_ratio)
            new_height = original_height
        else:
            new_width = original_width
            new_height = int(target_width / original_aspect_ratio)

        # Center crop dimensions
        x_center = new_width // 2
        y_center = new_height // 2
        crop_x1 = max(0, x_center - (target_width // 2))
        crop_y1 = max(0, y_center - (target_height // 2))
        crop_x2 = min(new_width, crop_x1 + target_width)
        crop_y2 = min(new_height, crop_y1 + target_height)

        # Create the output video writer
        if not output_path:
            processed_folder = os.path.join(os.getcwd(), 'processed_videos')
            os.makedirs(processed_folder, exist_ok=True)
            original_filename = os.path.basename(video_path)
            processed_filename = f"processed_aspect_ratio_{aspect_ratio}_{original_filename}"
            output_path = os.path.join(processed_folder, processed_filename)

        fourcc = cv2.VideoWriter_fourcc(*original_codec_name)
        out = cv2.VideoWriter(output_path, fourcc, frame_rate, (target_width, target_height))

        # Process the video frame by frame
        cap = cv2.VideoCapture(video_path)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Check if frame is empty
            if frame is None or frame.size == 0:
                print(f"Skipping empty frame at index {cap.get(cv2.CAP_PROP_POS_FRAMES)}")
                continue

            # Detect face and adjust cropping
            face = detect_face(frame)
            if face is not None:
                (x, y, w, h) = face
                x_center = x + w // 2
                y_center = y + h // 2
                crop_x1 = max(0, x_center - (target_width // 2))
                crop_y1 = max(0, y_center - (target_height // 2))
                crop_x2 = min(new_width, crop_x1 + target_width)
                crop_y2 = min(new_height, crop_y1 + target_height)
            else:
                crop_x1 = max(0, x_center - (target_width // 2))
                crop_y1 = max(0, y_center - (target_height // 2))
                crop_x2 = min(new_width, crop_x1 + target_width)
                crop_y2 = min(new_height, crop_y1 + target_height)

            # Resize and center crop the frame
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            cropped_frame = resized_frame[crop_y1:crop_y2, crop_x1:crop_x2]

            # Ensure the frame dimensions match the target size
            if cropped_frame.shape[0] != target_height or cropped_frame.shape[1] != target_width:
                cropped_frame = cv2.resize(cropped_frame, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)

            # Write the processed frame to the output video
            out.write(cropped_frame)

        cap.release()
        out.release()

        # Handle audio using MoviePy
        video_clip = VideoFileClip(video_path)
        audio = video_clip.audio
        final_video = VideoFileClip(output_path)
        final_video = final_video.set_audio(audio)
        final_output_path = output_path.replace('.mp4', '_final.mp4')
        final_video.write_videofile(final_output_path, codec="libx264", audio_codec="aac")

        return final_output_path
    except Exception as e:
        print(f"Error changing aspect ratio: {e}")
        return {"error in change aspect ratio": str(e)}
