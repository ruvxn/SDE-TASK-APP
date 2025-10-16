from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Project
from datetime import datetime

def register_project_routes(app):
    """Register project CRUD routes with the Flask app"""

    @app.route('/projects/create', methods=['GET', 'POST'])
    @login_required
    def create_project():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            deadline_str = request.form.get('deadline', '').strip()

            # Validation
            errors = []

            if not name or len(name) < 3:
                errors.append('Project name must be at least 3 characters long')

            # Parse deadline if provided
            deadline = None
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                except ValueError:
                    errors.append('Invalid deadline format')

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('create_project.html')

            # Create new project
            project = Project(
                name=name,
                description=description,
                deadline=deadline,
                user_id=current_user.id
            )
            db.session.add(project)
            db.session.commit()

            flash('Project created successfully!', 'success')
            return redirect(url_for('view_project', project_id=project.id))

        return render_template('create_project.html')

    @app.route('/projects/<int:project_id>')
    @login_required
    def view_project(project_id):
        project = Project.query.get_or_404(project_id)

        # Check if user owns this project
        if project.user_id != current_user.id:
            flash('You do not have permission to view this project', 'error')
            return redirect(url_for('dashboard'))

        # Get tasks sorted by creation date
        tasks = project.tasks
        return render_template('view_project.html', project=project, tasks=tasks)

    @app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_project(project_id):
        project = Project.query.get_or_404(project_id)

        # Check if user owns this project
        if project.user_id != current_user.id:
            flash('You do not have permission to edit this project', 'error')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            deadline_str = request.form.get('deadline', '').strip()

            # Validation
            errors = []

            if not name or len(name) < 3:
                errors.append('Project name must be at least 3 characters long')

            # Parse deadline if provided
            deadline = None
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                except ValueError:
                    errors.append('Invalid deadline format')

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('edit_project.html', project=project)

            # Update project
            project.name = name
            project.description = description
            project.deadline = deadline
            db.session.commit()

            flash('Project updated successfully!', 'success')
            return redirect(url_for('view_project', project_id=project.id))

        return render_template('edit_project.html', project=project)

    @app.route('/projects/<int:project_id>/delete', methods=['POST'])
    @login_required
    def delete_project(project_id):
        project = Project.query.get_or_404(project_id)

        # Check if user owns this project
        if project.user_id != current_user.id:
            flash('You do not have permission to delete this project', 'error')
            return redirect(url_for('dashboard'))

        project_name = project.name
        db.session.delete(project)
        db.session.commit()

        flash(f'Project "{project_name}" deleted successfully', 'success')
        return redirect(url_for('dashboard'))
