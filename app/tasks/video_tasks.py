# app/tasks/video_tasks.py

from app.extensions import db
from app.models.video import Video
import os
import time
import logging
from celery import shared_task
from celery.contrib.abortable import AbortableTask

@shared_task(bind=True, base=AbortableTask)
def process_video_task(self, video_id, file_path):
    try:
        video = Video.query.get(video_id)
        if not video:
            logging.error(f'Video with id {video_id} not found')
            return
        
        # Update status to queued
        video.status = Video.STATUS_QUEUED
        db.session.commit()

        # Simulate processing delay
        time.sleep(5)  # Simulate a delay before processing
        
        if self.is_aborted:
            print(f'Processing aborted for video_id: {video_id}')
            logging.info(f'Processing aborted for video_id: {video_id}')
            return

        # Update status to processing
        video.status = Video.STATUS_PROCESSING
        db.session.commit()

        # Simulate the video processing
        time.sleep(10)  # Replace with actual processing logic

        # Update status to completed
        video.status = Video.STATUS_COMPLETED
        db.session.commit()

        # Delete the processed file to clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logging.info(f'Completed processing for video_id: {video_id}')

    except Exception as e:
        logging.error(f'Error processing video_id: {video_id} - {str(e)}')
        video = Video.query.get(video_id)
        video.status = Video.STATUS_FAILED
        db.session.commit()
