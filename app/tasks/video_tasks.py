# 

from app.extensions import db
from app.models.video import Video, VideoOperation
import os
import logging
from flask import current_app
from celery import shared_task
from celery.contrib.abortable import AbortableTask
from datetime import datetime
import json  # For JSON serialization
from app.services.videos.create_clips import create_clips
from app.services.videos.merge_clips import merge_clips
from app.services.videos.change_aspect_ratio import change_aspect_ratio
from app.services.videos.add_logo import add_logo_to_video

@shared_task(bind=True, base=AbortableTask)
def process_video_task(self, video_id, filename, operations):
    video_operation = None
    try:
        # Define the upload path
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Get the video from the database
        video = Video.query.get(video_id)
        if not video:
            logging.error(f'Video with id {video_id} not found')
            return

        # Update video status to 'processing'
        video.status = Video.STATUS_PROCESSING
        db.session.commit()

        # Create a new operation log entry in the VideoOperation table
        video_operation = VideoOperation(
            video_id=video.id,
            task_id=self.request.id,  # Store the Celery task ID
            operation_name=operations.get("name"),
            operation_metadata=operations,
            status='processing',
            start_time=datetime.utcnow()
        )
        db.session.add(video_operation)
        db.session.commit()

        # Determine the operation type
        operation_name = operations.get("name")
        timestamps = operations.get("timestamps", [])
        
        # Perform the operation based on the type
        if operation_name == "clip":
            if not timestamps or len(timestamps) < 1:
                raise Exception("At least one timestamp is required for clipping.")
            if len(timestamps) > 10:
                raise Exception("Cannot process more than 10 clips.")
            
            # Perform the clipping operation
            clip_paths = create_clips(upload_path, timestamps)
            
            # Since clip_paths is a list, store it as JSON
            video.processed_path = json.dumps(clip_paths)  # Store list as JSON
            video_operation.result_path = json.dumps(clip_paths)  # Same for VideoOperation

        elif operation_name == "merge":
            if not timestamps or len(timestamps) < 2:
                raise Exception("At least two timestamps are required for merging.")
            if len(timestamps) > 10:
                raise Exception("Cannot merge more than 10 clips.")
            
            # Perform merging operation
            merged_clip_result = merge_clips(upload_path, timestamps)
            video.processed_path = merged_clip_result  # Single path for the merged video
            video_operation.result_path = merged_clip_result
        
        elif operation_name == "change_aspect_ratio":
            aspect_ratio = operations.get("aspect_ratio")
            if not aspect_ratio:
                raise Exception("Aspect ratio must be provided for changing aspect ratio.")
            valid_aspect_ratios = ["16:9", "9:16", "1:1", "4:3"]
            if aspect_ratio not in valid_aspect_ratios:
                raise Exception(f"Invalid aspect ratio. Valid options are: {', '.join(valid_aspect_ratios)}")
            
            # Perform aspect ratio change
            change_aspect_ratio(upload_path, aspect_ratio)
            video.processed_path = upload_path  # Assuming the path remains the same after processing
            video_operation.result_path = upload_path
        
        elif operation_name == "add_logo":
            logo_path = os.path.join(current_app.config['LOGO_FOLDER'], operations.get("logo_filename"))
            position = operations.get("position", "bottom_right")  # Default to 'bottom_right'
            
            # Perform logo addition
            result = add_logo_to_video(upload_path, logo_path, position)
            video.processed_path = result
            video_operation.result_path = result

        # Update the operation log entry with success details
        video_operation.status = 'completed'
        video_operation.end_time = datetime.utcnow()
        video_operation.duration = (video_operation.end_time - video_operation.start_time).total_seconds()
        db.session.commit()

        # Update the video status to 'completed'
        video.status = Video.STATUS_COMPLETED
        db.session.commit()

        # Clean up the upload path if needed
        if os.path.exists(upload_path):
            os.remove(upload_path)

        logging.info(f'Completed processing for video_id: {video_id}')

    except Exception as e:
        logging.error(f'Error processing video_id: {video_id} - {str(e)}')

        # Update the operation log entry with failure details
        if video_operation:
            video_operation.status = 'failed'
            video_operation.error_message = str(e)
            video_operation.end_time = datetime.utcnow()
            video_operation.duration = (video_operation.end_time - video_operation.start_time).total_seconds() if video_operation.start_time else None
            db.session.commit()

        # Mark the video status as failed
        video = Video.query.get(video_id)
        if video:
            video.status = Video.STATUS_FAILED
            db.session.commit()

        # Optionally, raise the error for Celery to retry the task
        raise self.retry(exc=e, countdown=60, max_retries=3)
