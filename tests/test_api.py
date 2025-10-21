import pytest
from models import db, User, Project, Task


@pytest.mark.integration
class TestProjectRoutes:
    def test_create_project_page_requires_auth(self, client):
        """Test create project page requires authentication"""
        response = client.get('/projects/create', follow_redirects=False)
        assert response.status_code in [302, 301]

    def test_create_project(self, authenticated_client, app):
        """Test creating a new project"""
        response = authenticated_client.post('/projects/create', data={
            'name': 'API Test Project',
            'description': 'Created via API test',
            'deadline': '2025-12-31'
        }, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            project = Project.query.filter_by(name='API Test Project').first()
            assert project is not None
            assert project.description == 'Created via API test'

    def test_view_project(self, authenticated_client, sample_project):
        """Test viewing a project"""
        response = authenticated_client.get(f'/projects/{sample_project}')
        assert response.status_code == 200
        assert b'Test Project' in response.data

    def test_view_nonexistent_project(self, authenticated_client):
        """Test viewing non-existent project returns 404"""
        response = authenticated_client.get('/projects/99999')
        assert response.status_code == 404

    def test_edit_project(self, authenticated_client, sample_project, app):
        """Test editing a project"""
        response = authenticated_client.post(f'/projects/{sample_project}/edit', data={
            'name': 'Updated Project Name',
            'description': 'Updated description',
            'deadline': '2026-01-01'
        }, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            project = Project.query.get(sample_project)
            assert project.name == 'Updated Project Name'
            assert project.description == 'Updated description'

    def test_delete_project(self, authenticated_client, sample_project, app):
        """Test deleting a project"""
        response = authenticated_client.post(f'/projects/{sample_project}/delete', follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            project = Project.query.get(sample_project)
            assert project is None


@pytest.mark.integration
class TestTaskRoutes:
    def test_create_task_requires_auth(self, client, sample_project):
        """Test create task requires authentication"""
        response = client.get(f'/projects/{sample_project}/tasks/create', follow_redirects=False)
        assert response.status_code in [302, 301]

    def test_create_task(self, authenticated_client, sample_project, app):
        """Test creating a new task"""
        response = authenticated_client.post(f'/projects/{sample_project}/tasks/create', data={
            'title': 'API Test Task',
            'description': 'Created via API test',
            'importance': 'high',
            'expected_completion_date': '2025-11-01'
        }, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            task = Task.query.filter_by(title='API Test Task').first()
            assert task is not None
            assert task.importance == 'high'

    def test_complete_task(self, authenticated_client, sample_task, app):
        """Test completing a task"""
        response = authenticated_client.post(f'/tasks/{sample_task}/complete', data={
            'is_completed': 'true'
        }, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            task = Task.query.get(sample_task)
            assert task.is_completed is True

    def test_edit_task(self, authenticated_client, sample_task, app):
        """Test editing a task"""
        response = authenticated_client.post(f'/tasks/{sample_task}/edit', data={
            'title': 'Updated Task Title',
            'description': 'Updated description',
            'importance': 'low',
            'expected_completion_date': '2025-12-01'
        }, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            task = Task.query.get(sample_task)
            assert task.title == 'Updated Task Title'
            assert task.importance == 'low'

    def test_delete_task(self, authenticated_client, sample_task, app):
        """Test deleting a task"""
        response = authenticated_client.post(f'/tasks/{sample_task}/delete', follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            task = Task.query.get(sample_task)
            assert task is None

    def test_complete_task_with_dependencies(self, authenticated_client, app):
        """Test completing task with unfulfilled dependencies"""
        with app.app_context():
            project = Project.query.filter_by(name='Test Project').first()
            if not project:
                user = User.query.filter_by(username='testuser').first()
                project = Project(
                    name='Test Project',
                    description='Test project description',
                    user_id=user.id
                )
                db.session.add(project)
                db.session.commit()

            task1 = Task(title='Dependency Task', project_id=project.id)
            task2 = Task(title='Dependent Task', project_id=project.id)
            db.session.add_all([task1, task2])
            db.session.commit()

            task2.dependencies.append(task1)
            db.session.commit()

            task2_id = task2.id

        response = authenticated_client.post(f'/tasks/{task2_id}/complete', follow_redirects=True)
        assert response.status_code == 200

        with app.app_context():
            task = Task.query.get(task2_id)
            assert task.is_completed is False


@pytest.mark.smoke
class TestSmokeTests:
    def test_app_runs(self, client):
        """Test application starts successfully"""
        response = client.get('/', follow_redirects=False)
        assert response.status_code in [200, 301, 302]

    def test_login_page_accessible(self, client):
        """Test login page is accessible"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_health_check(self, app):
        """Test basic app health"""
        assert app is not None
        assert app.config['TESTING'] is True
