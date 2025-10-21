import pytest
from datetime import datetime
from models import db, User, Project, Task


@pytest.mark.unit
class TestUserModel:
    def test_create_user(self, app):
        """Test creating a user"""
        with app.app_context():
            user = User(username='newuser', email='new@example.com')
            user.set_password('secret123')
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == 'newuser'
            assert user.email == 'new@example.com'
            assert user.password_hash is not None

    def test_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('mypassword')

            assert user.check_password('mypassword') is True
            assert user.check_password('wrongpassword') is False

    def test_unique_username(self, app, sample_user):
        """Test username uniqueness constraint"""
        with app.app_context():
            duplicate = User(username='testuser', email='different@example.com')
            duplicate.set_password('password')
            db.session.add(duplicate)

            with pytest.raises(Exception):
                db.session.commit()


@pytest.mark.unit
class TestProjectModel:
    def test_create_project(self, app, sample_user):
        """Test creating a project"""
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            project = Project(
                name='New Project',
                description='Project description',
                user_id=user.id
            )
            db.session.add(project)
            db.session.commit()

            assert project.id is not None
            assert project.name == 'New Project'
            assert project.user_id == user.id

    def test_completion_percentage_no_tasks(self, app, sample_project):
        """Test completion percentage with no tasks"""
        with app.app_context():
            project = Project.query.filter_by(name='Test Project').first()
            assert project.get_completion_percentage() == 0

    def test_completion_percentage_with_tasks(self, app, sample_project):
        """Test completion percentage calculation"""
        with app.app_context():
            project = Project.query.filter_by(name='Test Project').first()

            task1 = Task(title='Task 1', project_id=project.id, is_completed=True)
            task2 = Task(title='Task 2', project_id=project.id, is_completed=False)
            task3 = Task(title='Task 3', project_id=project.id, is_completed=True)
            task4 = Task(title='Task 4', project_id=project.id, is_completed=False)

            db.session.add_all([task1, task2, task3, task4])
            db.session.commit()

            assert project.get_completion_percentage() == 50

    def test_task_count(self, app, sample_project):
        """Test task count method"""
        with app.app_context():
            project = Project.query.filter_by(name='Test Project').first()

            task1 = Task(title='Task 1', project_id=project.id)
            task2 = Task(title='Task 2', project_id=project.id)
            db.session.add_all([task1, task2])
            db.session.commit()

            assert project.get_task_count() == 2


@pytest.mark.unit
class TestTaskModel:
    def test_create_task(self, app, sample_project):
        """Test creating a task"""
        with app.app_context():
            project = Project.query.filter_by(name='Test Project').first()
            task = Task(
                title='New Task',
                description='Task description',
                importance='high',
                project_id=project.id
            )
            db.session.add(task)
            db.session.commit()

            assert task.id is not None
            assert task.title == 'New Task'
            assert task.importance == 'high'
            assert task.is_completed is False

    def test_task_can_be_completed_no_dependencies(self, app, sample_task):
        """Test task completion without dependencies"""
        with app.app_context():
            task = Task.query.filter_by(title='Test Task').first()
            assert task.can_be_completed() is True

    def test_task_dependencies(self, app, sample_project):
        """Test task dependencies"""
        with app.app_context():
            project = Project.query.filter_by(name='Test Project').first()

            task1 = Task(title='Task 1', project_id=project.id)
            task2 = Task(title='Task 2', project_id=project.id)
            db.session.add_all([task1, task2])
            db.session.commit()

            task2.dependencies.append(task1)
            db.session.commit()

            assert task2.can_be_completed() is False

            task1.is_completed = True
            db.session.commit()

            assert task2.can_be_completed() is True

    def test_toggle_completion_without_dependencies(self, app, sample_task):
        """Test toggling task completion"""
        with app.app_context():
            task = Task.query.filter_by(title='Test Task').first()

            result = task.toggle_completion()
            assert result is True
            assert task.is_completed is True
            assert task.completed_at is not None

            result = task.toggle_completion()
            assert result is True
            assert task.is_completed is False
            assert task.completed_at is None

    def test_toggle_completion_with_dependencies(self, app, sample_project):
        """Test completion blocked by dependencies"""
        with app.app_context():
            project = Project.query.filter_by(name='Test Project').first()

            task1 = Task(title='Task 1', project_id=project.id)
            task2 = Task(title='Task 2', project_id=project.id)
            db.session.add_all([task1, task2])
            db.session.commit()

            task2.dependencies.append(task1)
            db.session.commit()

            result = task2.toggle_completion()
            assert result is False
            assert task2.is_completed is False
