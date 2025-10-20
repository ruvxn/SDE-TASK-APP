"""
Unit tests for database models
"""
import pytest
from datetime import datetime
from models import User, Project, Task
from werkzeug.security import generate_password_hash


@pytest.mark.unit
class TestUserModel:
    """Test User model functionality"""

    def test_create_user(self, db_session):
        """Test creating a new user"""
        user = User(
            username='newuser',
            email='newuser@example.com',
            password_hash=generate_password_hash('password')
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.created_at is not None

    def test_user_password_hashing(self, db_session):
        """Test password hashing functionality"""
        user = User(
            username='hashtest',
            email='hash@example.com',
            password_hash=generate_password_hash('testpass')
        )
        db_session.add(user)
        db_session.commit()

        # Password should be hashed
        assert user.password_hash != 'testpass'
        # Should be able to verify password
        from werkzeug.security import check_password_hash
        assert check_password_hash(user.password_hash, 'testpass')

    def test_user_projects_relationship(self, test_user, test_project, db_session):
        """Test user-project relationship"""
        assert test_project in test_user.projects
        assert test_project.owner == test_user


@pytest.mark.unit
class TestProjectModel:
    """Test Project model functionality"""

    def test_create_project(self, db_session, test_user):
        """Test creating a new project"""
        project = Project(
            name='New Project',
            description='Test description',
            user_id=test_user.id
        )
        db_session.add(project)
        db_session.commit()

        assert project.id is not None
        assert project.name == 'New Project'
        assert project.user_id == test_user.id

    def test_project_completion_percentage_empty(self, test_project):
        """Test completion percentage with no tasks"""
        # Remove any existing tasks
        test_project.tasks = []
        assert test_project.get_completion_percentage() == 0

    def test_project_completion_percentage(self, db_session, test_project):
        """Test completion percentage calculation"""
        # Create tasks
        task1 = Task(title='Task 1', is_completed=True, project_id=test_project.id)
        task2 = Task(title='Task 2', is_completed=False, project_id=test_project.id)
        task3 = Task(title='Task 3', is_completed=True, project_id=test_project.id)

        db_session.add_all([task1, task2, task3])
        db_session.commit()

        # 2 out of 3 tasks completed = 67%
        assert test_project.get_completion_percentage() == 67

    def test_project_task_count(self, db_session, test_project):
        """Test task count calculation"""
        # Create multiple tasks
        for i in range(5):
            task = Task(title=f'Task {i}', project_id=test_project.id)
            db_session.add(task)
        db_session.commit()

        assert test_project.get_task_count() == 5


@pytest.mark.unit
class TestTaskModel:
    """Test Task model functionality"""

    def test_create_task(self, db_session, test_project):
        """Test creating a new task"""
        task = Task(
            title='New Task',
            description='Task description',
            importance='high',
            project_id=test_project.id
        )
        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert task.title == 'New Task'
        assert task.importance == 'high'
        assert task.is_completed is False

    def test_task_completion_toggle(self, test_task):
        """Test toggling task completion"""
        assert test_task.is_completed is False

        # Complete the task
        result = test_task.toggle_completion()
        assert result is True
        assert test_task.is_completed is True
        assert test_task.completed_at is not None

        # Uncomplete the task
        result = test_task.toggle_completion()
        assert result is True
        assert test_task.is_completed is False

    def test_task_dependencies(self, db_session, test_project):
        """Test task dependency relationships"""
        task1 = Task(title='Task 1', project_id=test_project.id)
        task2 = Task(title='Task 2', project_id=test_project.id)

        db_session.add_all([task1, task2])
        db_session.commit()

        # Task2 depends on Task1
        task2.dependencies.append(task1)
        db_session.commit()

        assert task1 in task2.dependencies.all()

    def test_task_can_be_completed_with_dependencies(self, db_session, test_project):
        """Test that task cannot be completed if dependencies are not met"""
        task1 = Task(title='Dependency Task', is_completed=False, project_id=test_project.id)
        task2 = Task(title='Dependent Task', is_completed=False, project_id=test_project.id)

        db_session.add_all([task1, task2])
        db_session.commit()

        task2.dependencies.append(task1)
        db_session.commit()

        # Task2 cannot be completed because Task1 is not completed
        assert task2.can_be_completed() is False

        # Complete Task1
        task1.is_completed = True
        db_session.commit()

        # Now Task2 can be completed
        assert task2.can_be_completed() is True

    def test_task_toggle_with_unmet_dependencies(self, db_session, test_project):
        """Test that toggle fails when dependencies are not met"""
        task1 = Task(title='Dependency', is_completed=False, project_id=test_project.id)
        task2 = Task(title='Dependent', is_completed=False, project_id=test_project.id)

        db_session.add_all([task1, task2])
        db_session.commit()

        task2.dependencies.append(task1)
        db_session.commit()

        # Attempting to complete task2 should fail
        result = task2.toggle_completion()
        assert result is False
        assert task2.is_completed is False
