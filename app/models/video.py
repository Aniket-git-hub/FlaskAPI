# app/models/video.py

from app.extensions import db
from datetime import datetime

class Video(db.Model):
    __tablename__ = 'videos'

    STATUS_PENDING = 'pending'
    STATUS_QUEUED = 'queued'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(50), nullable=False, default=STATUS_PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Video {self.filename} - {self.status}>'
