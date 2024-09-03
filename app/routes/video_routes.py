# app/routes/video_routes.py

from flask import Blueprint, request, jsonify, current_app, render_template
from app.controllers.video_controller import upload_video_controller, get_video_status_controller
from app.models.video import Video

video_blueprint = Blueprint('video', __name__)

@video_blueprint.route('/', methods=['GET'])
def index():
    return render_template('pages/index.html')


@video_blueprint.route('/api/video', methods=['POST'])
def upload_video_route():
    return upload_video_controller(request)


@video_blueprint.route('/api/video/<int:video_id>', methods=['GET'])
def get_video_status_route(video_id):
    return get_video_status_controller(video_id)


@video_blueprint.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'SECRET_KEY': current_app.config['SECRET_KEY'],
        'SQLALCHEMY_DATABASE_URI': current_app.config['SQLALCHEMY_DATABASE_URI'],
        'CELERY_BROKER_URL': current_app.config['CELERY_BROKER_URL'],
        'UPLOAD_FOLDER': current_app.config['UPLOAD_FOLDER']
    })
    

@video_blueprint.route('/api/db-test', methods=['GET'])
def db_test():
    try:
        video_count = Video.query.count()
        return jsonify({"message": f"Database connected successfully. Video count: {video_count}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@video_blueprint.app_errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html'), 404