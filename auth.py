from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

def register_auth_routes(app):
    """Register authentication routes with the Flask app"""

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        #redirect IF already logged in
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            # Validation
            errors = []

            if not username or len(username) < 3:
                errors.append('Username must be at least 3 characters long')

            if not email or '@' not in email:
                errors.append('Please enter a valid email address')

            if not password or len(password) < 6:
                errors.append('Password must be at least 6 characters long')

            if password != confirm_password:
                errors.append('Passwords do not match')

            #Check if user already exists
            if User.query.filter_by(username=username).first():
                errors.append('Username already exists')

            if User.query.filter_by(email=email).first():
                errors.append('Email already registered')

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('register.html')

            #Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        #Redirect if already logged in
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            # Validation
            if not username or not password:
                flash('Please enter both username and password', 'error')
                return render_template('login.html')

            # Find user and check password
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                flash('Login successful!', 'success')
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
                return render_template('login.html')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'success')
        return redirect(url_for('login'))

    @app.route('/')
    def index():
        # Redirect to dashboard if logged in, otherwise to login
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get users projects
        projects = current_user.projects
        return render_template('dashboard.html', projects=projects)
