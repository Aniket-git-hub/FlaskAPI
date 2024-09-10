import cv2
import numpy as np
import os

def validate_aspect_ratio(aspect_ratio):
    valid_aspect_ratios = ["16:9", "9:16", "1:1", "4:3"]
    if aspect_ratio not in valid_aspect_ratios:
        raise ValueError(f"Invalid aspect ratio. Valid options are: {', '.join(valid_aspect_ratios)}")

def calculate_new_dimensions(aspect_ratio, original_width, original_height):
    target_width, target_height = {
        "16:9": (16, 9),
        "9:16": (9, 16),
        "1:1": (1, 1),
        "4:3": (4, 3),
    }.get(aspect_ratio, (16, 9))

    target_aspect_ratio = target_width / target_height
    original_aspect_ratio = original_width / original_height

    if original_aspect_ratio > target_aspect_ratio:
        new_width = int(target_height * original_aspect_ratio)
        new_height = original_height
    else:
        new_width = original_width
        new_height = int(target_width / original_aspect_ratio)

    return new_width, new_height

def change_aspect_ratio(video_path, aspect_ratio, output_path=None):
    """
    Function to change the aspect ratio of the video while keeping the subject centered,
    and save the processed video in the processed folder.

    Args:
    video_path (str): Path to the input video file.
    aspect_ratio (str): Desired aspect ratio (e.g., "16:9", "9:16", "1:1", "4:3").
    output_path (str, optional): Path to the output video file. If not provided, it will be saved in the 'processed_videos' folder.

    Returns:
    str: Path to the processed video file.
    """
    try:
        # Validate aspect ratio
        validate_aspect_ratio(aspect_ratio)

        # Open the video with OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Failed to open video file. The video might be corrupted or in an unsupported format.")
        
        ret, frame = cap.read()
        if not ret or frame is None:
            raise ValueError("Failed to read the first frame from the video. The video might be corrupted or in an unsupported format.")

        # Get video properties
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        original_codec = int(cap.get(cv2.CAP_PROP_FOURCC))
        original_codec_name = ''.join(chr(int(c)) for c in [original_codec & 0xFF, (original_codec >> 8) & 0xFF, (original_codec >> 16) & 0xFF, (original_codec >> 24) & 0xFF])
        cap.release()

        # Calculate new dimensions
        new_width, new_height = calculate_new_dimensions(aspect_ratio, original_width, original_height)

        # Center crop dimensions
        x_center = new_width // 2
        y_center = new_height // 2
        crop_x1 = x_center - (original_width // 2)
        crop_y1 = y_center - (original_height // 2)
        crop_x2 = crop_x1 + original_width
        crop_y2 = crop_y1 + original_height

        # Create the output video writer
        if not output_path:
            processed_folder = os.path.join(os.getcwd(), 'processed_videos')
            os.makedirs(processed_folder, exist_ok=True)
            original_filename = os.path.basename(video_path)
            processed_filename = f"processed_aspect_ratio_{aspect_ratio}_{original_filename}"
            output_path = os.path.join(processed_folder, processed_filename)

        fourcc = cv2.VideoWriter_fourcc(*original_codec_name)
        out = cv2.VideoWriter(output_path, fourcc, frame_rate, (new_width, new_height))

        # Process the video frame by frame
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Failed to open video file for processing.")
        
        for frame_idx in range(total_frames):
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            # Resize and center crop the frame
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            cropped_frame = resized_frame[crop_y1:crop_y2, crop_x1:crop_x2]

            # Write the processed frame to the output video
            out.write(cropped_frame)

        cap.release()
        out.release()

        return output_path

    except Exception as e:
        print(f"Error changing aspect ratio: {e}")
        raise Exception(f"Error in change aspect ratio: {e}")
        
