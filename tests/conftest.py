import os
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["FLASK_ENV"] = "testing"

from run import create_app
from models import db, User, Project, Task


@pytest.fixture
def app():
    """Create and configure app for testing"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for making requests"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    return user_id


@pytest.fixture
def authenticated_client(client, sample_user):
    """Client with authenticated user session"""
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    return client


@pytest.fixture
def sample_project(app, sample_user):
    """Create a sample project"""
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        project = Project(
            name='Test Project',
            description='Test project description',
            user_id=user.id
        )
        db.session.add(project)
        db.session.commit()
        project_id = project.id

    return project_id


@pytest.fixture
def sample_task(app, sample_project):
    """Create a sample task"""
    with app.app_context():
        project = Project.query.filter_by(name='Test Project').first()
        task = Task(
            title='Test Task',
            description='Test task description',
            importance='high',
            project_id=project.id
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    return task_id
