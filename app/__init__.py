import logging
from flask import Flask, request
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, make_celery
from app.routes.video_routes import video_blueprint

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    if not app.debug:
        # In production, log to a file
        # file_handler = logging.FileHandler('app.log')
        print("In Production")
        # file_handler.setLevel(logging.INFO)
        # file_handler.setFormatter(logging.Formatter(
        #     '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        # ))
        # app.logger.addHandler(file_handler)
    else:
        # In development, log to console
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(stream_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask app startup')

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["https://apitester.letsbug.in", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        },
        r"/*": {
            "origins": "*",  # Allow all origins for non-api routes
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    celery = make_celery(app)
    celery.set_default()

    # Register blueprints
    app.register_blueprint(video_blueprint)

    @app.after_request
    def after_request(response):
        # For non-API routes, allow all origins
        if not request.path.startswith('/api/'):
            response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    return app, celery

app, celery = create_app()
app.app_context().push()

if __name__ == "__main__":
    app.run(debug=True)