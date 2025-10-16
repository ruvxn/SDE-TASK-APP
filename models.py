from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# many 2 many- assoication table for dependeices
task_dependencies = db.Table('task_dependencies',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('depends_on_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    #relationship to projects
    projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    #relationship to tasks
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')

    def get_completion_percentage(self):
        """Calculate project completion based on completed tasks"""
        if not self.tasks:
            return 0
        completed = sum(1 for task in self.tasks if task.is_completed)
        return round((completed / len(self.tasks)) * 100)

    def get_task_count(self):
        """Get total number of tasks in this project"""
        return len(self.tasks)

    def __repr__(self):
        return f'<Project {self.name}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_completion_date = db.Column(db.DateTime)
    importance = db.Column(db.String(20), default='medium')  # importance can be set to low, medium, high
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    #Self referential many-to-many relationship for dependencies
    dependencies = db.relationship(
        'Task',
        secondary=task_dependencies,
        primaryjoin=(task_dependencies.c.task_id == id),
        secondaryjoin=(task_dependencies.c.depends_on_id == id),
        backref=db.backref('dependent_tasks', lazy='dynamic'),
        lazy='dynamic'
    )

    def can_be_completed(self):
        """Check if all dependency tasks are completed"""
        return all(dep.is_completed for dep in self.dependencies)

    def toggle_completion(self):
        """Toggle task completion status"""
        if not self.is_completed and not self.can_be_completed():
            return False  # this will ensure that a task cannot be completed when a dependancy is not met

        self.is_completed = not self.is_completed
        self.completed_at = datetime.utcnow() if self.is_completed else None
        return True

    def __repr__(self):
        return f'<Task {self.title}>'
