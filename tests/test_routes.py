"""
Integration tests for project and task routes
"""
import pytest
from models import Project, Task


@pytest.mark.integration
class TestProjectRoutes:
    """Test project management routes"""

    def test_dashboard_requires_auth(self, client):
        """Test that dashboard requires authentication"""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    def test_dashboard_loads_for_authenticated_user(self, authenticated_client):
        """Test that authenticated users can access dashboard"""
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Project' in response.data

    def test_create_project(self, authenticated_client, db_session):
        """Test creating a new project"""
        response = authenticated_client.post('/project/create', data={
            'name': 'Test Project',
            'description': 'A test project'
        }, follow_redirects=True)

        assert response.status_code == 200

        # Verify project was created
        project = db_session.query(Project).filter_by(name='Test Project').first()
        assert project is not None
        assert project.description == 'A test project'

    def test_view_project(self, authenticated_client, test_project):
        """Test viewing a project"""
        response = authenticated_client.get(f'/project/{test_project.id}')
        assert response.status_code == 200
        assert test_project.name.encode() in response.data

    def test_edit_project(self, authenticated_client, test_project, db_session):
        """Test editing a project"""
        response = authenticated_client.post(f'/project/{test_project.id}/edit', data={
            'name': 'Updated Project',
            'description': 'Updated description'
        }, follow_redirects=True)

        assert response.status_code == 200

        # Verify project was updated
        db_session.refresh(test_project)
        assert test_project.name == 'Updated Project'

    def test_delete_project(self, authenticated_client, test_project, db_session):
        """Test deleting a project"""
        project_id = test_project.id
        response = authenticated_client.post(f'/project/{project_id}/delete', follow_redirects=True)

        assert response.status_code == 200

        # Verify project was deleted
        project = db_session.query(Project).filter_by(id=project_id).first()
        assert project is None


@pytest.mark.integration
class TestTaskRoutes:
    """Test task management routes"""

    def test_create_task(self, authenticated_client, test_project, db_session):
        """Test creating a new task"""
        response = authenticated_client.post(f'/project/{test_project.id}/task/create', data={
            'title': 'New Task',
            'description': 'Task description',
            'importance': 'high'
        }, follow_redirects=True)

        assert response.status_code == 200

        # Verify task was created
        task = db_session.query(Task).filter_by(title='New Task').first()
        assert task is not None
        assert task.project_id == test_project.id

    def test_edit_task(self, authenticated_client, test_task, db_session):
        """Test editing a task"""
        response = authenticated_client.post(f'/task/{test_task.id}/edit', data={
            'title': 'Updated Task',
            'description': 'Updated description',
            'importance': 'low'
        }, follow_redirects=True)

        assert response.status_code == 200

        # Verify task was updated
        db_session.refresh(test_task)
        assert test_task.title == 'Updated Task'

    def test_toggle_task_completion(self, authenticated_client, test_task, db_session):
        """Test toggling task completion"""
        assert test_task.is_completed is False

        response = authenticated_client.post(f'/task/{test_task.id}/toggle', follow_redirects=True)
        assert response.status_code == 200

        # Verify task was completed
        db_session.refresh(test_task)
        assert test_task.is_completed is True

    def test_delete_task(self, authenticated_client, test_task, db_session):
        """Test deleting a task"""
        task_id = test_task.id
        response = authenticated_client.post(f'/task/{task_id}/delete', follow_redirects=True)

        assert response.status_code == 200

        # Verify task was deleted
        task = db_session.query(Task).filter_by(id=task_id).first()
        assert task is None

    def test_task_with_dependencies(self, authenticated_client, test_project, db_session):
        """Test creating tasks with dependencies"""
        # Create first task
        task1 = Task(title='Task 1', completed=False, project_id=test_project.id)
        db_session.add(task1)
        db_session.commit()

        # Create second task that depends on first
        response = authenticated_client.post(f'/project/{test_project.id}/task/create', data={
            'title': 'Task 2',
            'description': 'Depends on Task 1',
            'importance': 'medium',
            'dependencies': [task1.id]
        }, follow_redirects=True)

        # The response might vary based on implementation
        # Just verify we get a valid response
        assert response.status_code == 200


@pytest.mark.integration
class TestApplicationHealth:
    """Test application health and basic functionality"""

    def test_index_page(self, client):
        """Test that index page redirects to login"""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    def test_404_handling(self, client):
        """Test that non-existent routes return 404"""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404

    def test_database_connection(self, app):
        """Test that database connection works"""
        with app.app_context():
            from models import db
            # This will raise an exception if connection fails
            db.session.execute(db.text('SELECT 1'))
