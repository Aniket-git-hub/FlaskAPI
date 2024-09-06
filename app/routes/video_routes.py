# app/routes/video_routes.py

from flask import Blueprint, request, jsonify, current_app, render_template
from app.controllers.video_controller import upload_video_controller, get_video_status_controller, abort_video_processing_controller, get_all_videos_controller
from app.models.video import Video

video_blueprint = Blueprint('video', __name__)

@video_blueprint.route('/', methods=['GET'])
def index():
    return render_template('pages/index.html')


@video_blueprint.route('/api/video', methods=['POST'])
def upload_video_route():
    return upload_video_controller(request)


@video_blueprint.route('/api/video/<int:task_id>', methods=['GET'])
def get_video_status_route(task_id):
    return get_video_status_controller(task_id)
  

@video_blueprint.route('/api/video/abort/<string:task_id>', methods=['POST'])
def abort_video_processing_route(task_id):
    return abort_video_processing_controller(task_id)


@video_blueprint.route('/api/videos', methods=['GET'])
def get_all_videos_route():
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    return get_all_videos_controller(status, page, per_page)


@video_blueprint.app_errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html'), 404