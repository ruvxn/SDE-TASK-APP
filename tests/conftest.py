"""
Pytest configuration and fixtures for testing
"""
import pytest
import os

# Set environment variables BEFORE importing the app
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'  # Use in-memory SQLite for tests

from run import create_app
from models import db, User, Project, Task


@pytest.fixture(scope='session')
def app():
    """Create and configure a test application instance."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    # Create tables
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a new database session for each test."""
    with app.app_context():
        # Clear any existing data
        db.session.remove()

        # Create fresh tables
        db.create_all()

        yield db.session

        # Cleanup after test
        db.session.rollback()
        db.drop_all()
        db.session.remove()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from werkzeug.security import generate_password_hash

    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('password123')
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_project(db_session, test_user):
    """Create a test project."""
    project = Project(
        name='Test Project',
        description='A test project for unit testing',
        user_id=test_user.id
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def test_task(db_session, test_project):
    """Create a test task."""
    task = Task(
        title='Test Task',
        description='A test task',
        importance='high',
        is_completed=False,
        project_id=test_project.id
    )
    db_session.add(task)
    db_session.commit()
    return task


@pytest.fixture
def authenticated_client(client, test_user):
    """Return a client with an authenticated user session."""
    with client:
        client.post('/login', data={
            'username': test_user.username,
            'password': 'password123'
        }, follow_redirects=True)
        yield client
