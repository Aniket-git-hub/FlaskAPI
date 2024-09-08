# app/controllers/video_controller.py

from app.models.video import Video, VideoOperation
from app.extensions import db
from app.tasks.video_tasks import process_video_task
from flask import jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
from pathlib import Path

def upload_video_controller(request):
    logger = current_app.logger

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    operations = request.form.get('operations')
    if not operations:
        return jsonify({'error': 'No operations provided'}), 400
    
    try:
        logger.info(operations)
        operations = json.loads(operations)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid operations format'}), 400
    
    # Ensure upload and logo directories exist
    upload_folder = current_app.config['UPLOAD_FOLDER']
    logo_folder = current_app.config['LOGO_FOLDER']

    # Convert to absolute paths
    upload_folder = os.path.abspath(upload_folder)
    logo_folder = os.path.abspath(logo_folder)

    logger.info(f"Attempting to create upload folder: {upload_folder}")
    Path(upload_folder).mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload folder created/exists: {os.path.exists(upload_folder)}")

    logger.info(f"Attempting to create logo folder: {logo_folder}")
    Path(logo_folder).mkdir(parents=True, exist_ok=True)
    logger.info(f"Logo folder created/exists: {os.path.exists(logo_folder)}")

    # Save uploaded file
    filename = secure_filename(file.filename)
    upload_path = os.path.join(upload_folder, filename)
    file.save(upload_path)
    logger.info(f"Saved uploaded file to: {upload_path}")

    # Handle logo file if present
    if 'logo' in request.files:
        logo_file = request.files['logo']
        if logo_file.filename != '':
            logo_filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(logo_folder, logo_filename)
            logo_file.save(logo_path)
            logger.info(f"Saved logo file to: {logo_path}")
            
            if operations.get('name') == 'add_logo':
                operations['logo_filename'] = logo_filename
                logger.info(f"Updated operations with logo path: {logo_path}")

    # Log current working directory and final paths
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Upload folder config: {current_app.config['UPLOAD_FOLDER']}")
    logger.info(f"Logo folder config: {current_app.config['LOGO_FOLDER']}")
    logger.info(f"Final upload path: {upload_path}")
    logger.info(f"Final logo path: {logo_path if 'logo' in request.files and logo_file.filename != '' else 'No logo uploaded'}")

    # Verify file existence
    if not os.path.exists(upload_path):
        logger.error(f"Uploaded file not found: {upload_path}")
        return jsonify({'error': f'Uploaded file not found: {upload_path}'}), 404

    if 'logo' in request.files and logo_file.filename != '' and not os.path.exists(logo_path):
        logger.error(f"Logo file not found: {logo_path}")
        return jsonify({'error': f'Logo file not found: {logo_path}'}), 404

    # Save record to the database
    video = Video(filename=filename, status=Video.STATUS_QUEUED)
    db.session.add(video)
    db.session.commit()

    # Assign the task to Celery
    result = process_video_task.delay(video.id, upload_path, operations)

    logger.info(f"Video processing task created with ID: {result.id}")

    return jsonify({'message': 'File uploaded successfully', 'video_id': video.id, 'task_id': result.id}), 201


def get_all_videos_controller(status=None, page=1, per_page=10):
    query = Video.query
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    videos = pagination.items
    total_videos = pagination.total
    total_pages = pagination.pages
    current_page = pagination.page
    
    videos_data = []
    
    for video in videos:
        # Get the number of operations performed on this video
        operations_count = VideoOperation.query.filter_by(video_id=video.id).count()

        # If the video failed, we might want to include the error message from the last failed operation
        last_operation = VideoOperation.query.filter_by(video_id=video.id).order_by(VideoOperation.id.desc()).first()
        error_message = last_operation.error_message if last_operation and last_operation.status == 'failed' else None

        # Prepare video data
        video_info = {
            'video_id': video.id,
            'filename': video.filename,
            'status': video.status,
            'created_at': video.created_at.isoformat(),
            'updated_at': video.updated_at.isoformat(),
            'processed_path': video.processed_path,
            'operations_count': operations_count,
            'error_message': error_message  # Include error message if available
        }

        videos_data.append(video_info)

    return jsonify({
        'videos': videos_data,
        'total_videos': total_videos,
        'total_pages': total_pages,
        'current_page': current_page,
        'per_page': per_page
    }), 200


def get_video_operations_controller(video_id, page=1, per_page=10):
    video = Video.query.get_or_404(video_id)

    # Get all operations for the given video
    query = VideoOperation.query.filter_by(video_id=video_id).order_by(VideoOperation.id.asc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    operations = pagination.items
    total_operations = pagination.total
    total_pages = pagination.pages
    current_page = pagination.page
    
    operations_data = [{
        'operation_name': operation.operation_name,
        'status': operation.status,
        'start_time': operation.start_time.isoformat() if operation.start_time else None,
        'end_time': operation.end_time.isoformat() if operation.end_time else None,
        'duration': operation.duration,
        'result_path': operation.result_path,
        'error_message': operation.error_message
    } for operation in operations]

    return jsonify({
        'video_id': video.id,
        'filename': video.filename,
        'operations': operations_data,
        'total_operations': total_operations,
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
