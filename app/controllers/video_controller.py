# app/controllers/video_controller.py

from app.models.video import Video
from app.extensions import db
from app.tasks.video_tasks import process_video_task
from flask import jsonify, current_app
from werkzeug.utils import secure_filename
import os

def upload_video_controller(request):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)

    # Save record to the database
    video = Video(filename=filename, status=Video.STATUS_QUEUED)
    db.session.add(video)
    db.session.commit()

    # Assign the task to Celery
    current_app.celery.send_task('app.tasks.video_tasks.process_video_task', args=[video.id, upload_path])

    return jsonify({'message': 'File uploaded successfully', 'video_id': video.id}), 201

def get_video_status_controller(video_id):
    video = Video.query.get_or_404(video_id)
    return jsonify({
        'video_id': video.id,
        'filename': video.filename,
        'status': video.status,
        'created_at': video.created_at.isoformat(),
        'updated_at': video.updated_at.isoformat()
    }), 200

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
