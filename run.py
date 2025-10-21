from flask import Flask
from flask_login import LoginManager
from prometheus_flask_exporter import PrometheusMetrics
from models import db, User
from config import Config
from auth import register_auth_routes
from projects import register_project_routes
from tasks import register_task_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Prometheus metrics (skip in test mode to avoid duplicate registration)
    if not app.config.get('TESTING', False):
        metrics = PrometheusMetrics(app)
        # Add default metrics: request count, duration, and info
        metrics.info('app_info', 'Application info', version='1.0.0')

    # Initialize database
    db.init_app(app)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register routes
    register_auth_routes(app)
    register_project_routes(app)
    register_task_routes(app)

    # Create tables if they don't exist already
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
