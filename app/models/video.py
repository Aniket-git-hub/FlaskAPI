# app/models/video.py

from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Video(db.Model):
    __tablename__ = 'videos'

    STATUS_PENDING = 'pending'
    STATUS_QUEUED = 'queued'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # The uploaded video file name
    task_id = db.Column(db.String(255), nullable=True)  # The uploaded video file name
    status = db.Column(db.String(20), nullable=False, default='pending')  # Status of the video processing (queued, processing, completed, failed)
    processed_path = db.Column(db.String(255), nullable=True)  # Path to the final processed video
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp when the video was uploaded
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Timestamp when the video was last updated

    # Relationship to track detailed logs of each operation
    operations_log = db.relationship('VideoOperation', backref='video', lazy=True)

    def __repr__(self):
        return f'<Video {self.filename} - {self.status}>'


class VideoOperation(db.Model):
    __tablename__ = 'video_operations'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)  # Reference to the associated video
    task_id = db.Column(db.String(255), nullable=True)  # The uploaded video file name
    operation_name = db.Column(db.String(50), nullable=False)  # Name of the operation (e.g., clip, merge, caption)
    operation_metadata = db.Column(JSON, nullable=True)  # Additional metadata for each operation (e.g., timestamps, aspect ratio)
    status = db.Column(db.String(20), nullable=False, default='pending')  # Status of the operation (queued, processing, completed, failed)
    start_time = db.Column(db.DateTime, nullable=True)  # When the operation started
    end_time = db.Column(db.DateTime, nullable=True)  # When the operation finished
    duration = db.Column(db.Integer, nullable=True)  # Time taken for the operation (in seconds)
    result_path = db.Column(db.String(255), nullable=True)  # Path to the intermediate result of this operation
    error_message = db.Column(db.Text, nullable=True)  # Error message if the operation failed

    def __repr__(self):
        return f"<VideoOperation {self.operation_name} - {self.status}>"