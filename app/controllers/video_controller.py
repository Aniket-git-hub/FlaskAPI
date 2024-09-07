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
    result = process_video_task.delay(video.id, upload_path)

    return jsonify({'message': 'File uploaded successfully', 'video_id': video.id, 'id': result.id}), 201


def get_all_videos_controller(status=None, page=1, per_page=10):
    query = Video.query
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    videos = pagination.items
    total_videos = pagination.total
    total_pages = pagination.pages
    current_page = pagination.page
    
    videos_data = [{
        'video_id': video.id,
        'filename': video.filename,
        'status': video.status,
        'created_at': video.created_at.isoformat(),
        'updated_at': video.updated_at.isoformat()
    } for video in videos]
    
    return jsonify({
        'videos': videos_data,
        'total_videos': total_videos,
        'total_pages': total_pages,
        'current_page': current_page,
        'per_page': per_page
    }), 200



def abort_video_processing_controller(task_id): 
    task = process_video_task.AsyncResult(task_id)
    task.abort()
    return jsonify({'message': 'Video Processing Aborted'}), 200
    

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
