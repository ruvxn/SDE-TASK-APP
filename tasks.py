from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Project, Task
from datetime import datetime

def register_task_routes(app):
    """Register task CRUD routes with the Flask app"""

    @app.route('/projects/<int:project_id>/tasks/create', methods=['GET', 'POST'])
    @login_required
    def create_task(project_id):
        project = Project.query.get_or_404(project_id)

        # Check if user owns this project
        if project.user_id != current_user.id:
            flash('You do not have permission to add tasks to this project', 'error')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            start_date_str = request.form.get('start_date', '').strip()
            expected_completion_str = request.form.get('expected_completion_date', '').strip()
            importance = request.form.get('importance', 'medium')
            dependency_ids = request.form.getlist('dependencies')

            # Validation
            errors = []

            if not title or len(title) < 3:
                errors.append('Task title must be at least 3 characters long')

            if importance not in ['low', 'medium', 'high']:
                errors.append('Invalid importance level')

            # Parse dates
            start_date = None
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                except ValueError:
                    errors.append('Invalid start date format')

            expected_completion = None
            if expected_completion_str:
                try:
                    expected_completion = datetime.strptime(expected_completion_str, '%Y-%m-%d')
                except ValueError:
                    errors.append('Invalid expected completion date format')

            # Validate dependencies exist and belong to same project
            dependencies = []
            if dependency_ids:
                for dep_id in dependency_ids:
                    dep_task = Task.query.get(int(dep_id))
                    if not dep_task or dep_task.project_id != project_id:
                        errors.append(f'Invalid dependency task ID: {dep_id}')
                    else:
                        dependencies.append(dep_task)

            if errors:
                for error in errors:
                    flash(error, 'error')
                # Get available tasks for dependencies
                available_tasks = Task.query.filter_by(project_id=project_id).all()
                return render_template('create_task.html', project=project,
                                     available_tasks=available_tasks)

            # Create new task
            task = Task(
                title=title,
                description=description,
                start_date=start_date or datetime.utcnow(),
                expected_completion_date=expected_completion,
                importance=importance,
                project_id=project_id
            )
            db.session.add(task)
            db.session.flush()  # Get task ID before adding dependencies

            # Add dependencies
            for dep_task in dependencies:
                task.dependencies.append(dep_task)

            db.session.commit()

            flash('Task created successfully!', 'success')
            return redirect(url_for('view_project', project_id=project_id))

        # Get available tasks for dependencies
        available_tasks = Task.query.filter_by(project_id=project_id).all()
        return render_template('create_task.html', project=project,
                             available_tasks=available_tasks)

    @app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_task(task_id):
        task = Task.query.get_or_404(task_id)
        project = task.project

        # Check if user owns this project
        if project.user_id != current_user.id:
            flash('You do not have permission to edit this task', 'error')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            start_date_str = request.form.get('start_date', '').strip()
            expected_completion_str = request.form.get('expected_completion_date', '').strip()
            importance = request.form.get('importance', 'medium')
            dependency_ids = request.form.getlist('dependencies')

            # Validation
            errors = []

            if not title or len(title) < 3:
                errors.append('Task title must be at least 3 characters long')

            if importance not in ['low', 'medium', 'high']:
                errors.append('Invalid importance level')

            # Parse dates
            start_date = None
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                except ValueError:
                    errors.append('Invalid start date format')

            expected_completion = None
            if expected_completion_str:
                try:
                    expected_completion = datetime.strptime(expected_completion_str, '%Y-%m-%d')
                except ValueError:
                    errors.append('Invalid expected completion date format')

            # Validate dependencies - cannot depend on itself
            dependencies = []
            if dependency_ids:
                for dep_id in dependency_ids:
                    dep_id_int = int(dep_id)
                    if dep_id_int == task_id:
                        errors.append('Task cannot depend on itself')
                        continue
                    dep_task = Task.query.get(dep_id_int)
                    if not dep_task or dep_task.project_id != project.id:
                        errors.append(f'Invalid dependency task ID: {dep_id}')
                    else:
                        # Check for circular dependencies
                        if would_create_circular_dependency(task, dep_task):
                            errors.append(f'Cannot add dependency on "{dep_task.title}" - would create circular dependency')
                        else:
                            dependencies.append(dep_task)

            if errors:
                for error in errors:
                    flash(error, 'error')
                # Get available tasks for dependencies (exclude self)
                available_tasks = Task.query.filter(
                    Task.project_id == project.id,
                    Task.id != task_id
                ).all()
                return render_template('edit_task.html', task=task, project=project,
                                     available_tasks=available_tasks)

            # Update task
            task.title = title
            task.description = description
            task.start_date = start_date or task.start_date
            task.expected_completion_date = expected_completion
            task.importance = importance

            # Update dependencies - clear and re-add
            task.dependencies = []
            for dep_task in dependencies:
                task.dependencies.append(dep_task)

            db.session.commit()

            flash('Task updated successfully!', 'success')
            return redirect(url_for('view_project', project_id=project.id))

        # Get available tasks for dependencies (exclude self)
        available_tasks = Task.query.filter(
            Task.project_id == project.id,
            Task.id != task_id
        ).all()
        return render_template('edit_task.html', task=task, project=project,
                             available_tasks=available_tasks)

    @app.route('/tasks/<int:task_id>/delete', methods=['POST'])
    @login_required
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        project = task.project

        # Check if user owns this project
        if project.user_id != current_user.id:
            flash('You do not have permission to delete this task', 'error')
            return redirect(url_for('dashboard'))

        # Check if other tasks depend on this one
        dependent_tasks = task.dependent_tasks.all()
        if dependent_tasks:
            dependent_titles = [t.title for t in dependent_tasks]
            flash(f'Cannot delete task. The following tasks depend on it: {", ".join(dependent_titles)}', 'error')
            return redirect(url_for('view_project', project_id=project.id))

        task_title = task.title
        db.session.delete(task)
        db.session.commit()

        flash(f'Task "{task_title}" deleted successfully', 'success')
        return redirect(url_for('view_project', project_id=project.id))

    @app.route('/tasks/<int:task_id>/complete', methods=['POST'])
    @login_required
    def complete_task(task_id):
        task = Task.query.get_or_404(task_id)
        project = task.project

        # Check if user owns this project
        if project.user_id != current_user.id:
            flash('You do not have permission to modify this task', 'error')
            return redirect(url_for('dashboard'))

        # Get the completion status from form
        is_completed = request.form.get('is_completed') == 'true'

        if is_completed:
            # Check if dependencies are met
            if not task.can_be_completed():
                flash('Cannot complete task. All dependency tasks must be completed first.', 'error')
                return redirect(url_for('view_project', project_id=project.id))

            task.is_completed = True
            task.completed_at = datetime.utcnow()
            flash(f'Task "{task.title}" marked as completed!', 'success')
        else:
            # Uncompleting - check if other tasks depend on this and are completed
            dependent_completed = [t for t in task.dependent_tasks.all() if t.is_completed]
            if dependent_completed:
                dependent_titles = [t.title for t in dependent_completed]
                flash(f'Cannot mark as incomplete. The following completed tasks depend on it: {", ".join(dependent_titles)}', 'error')
                return redirect(url_for('view_project', project_id=project.id))

            task.is_completed = False
            task.completed_at = None
            flash(f'Task "{task.title}" marked as incomplete', 'success')

        db.session.commit()
        return redirect(url_for('view_project', project_id=project.id))


def would_create_circular_dependency(task, new_dependency):
    """Check if adding new_dependency to task would create a circular dependency"""
    # If new_dependency already depends on task (directly or indirectly), it's circular
    visited = set()

    def has_path_to_task(current_task):
        if current_task.id == task.id:
            return True
        if current_task.id in visited:
            return False
        visited.add(current_task.id)

        for dep in current_task.dependencies:
            if has_path_to_task(dep):
                return True
        return False

    return has_path_to_task(new_dependency)
