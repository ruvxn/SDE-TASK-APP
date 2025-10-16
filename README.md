# Project Management Application

A simple web-based project management application built with Flask and PostgreSQL.

## Features

- **User Authentication** - Secure registration and login
- **Project Management** - Create, read, update, delete projects
- **Task Management** - Tasks with dependencies and importance levels
- **Dependency Tracking** - Tasks must be completed in order
- **Circular Dependency Prevention** - Smart validation prevents cycles
- **Progress Calculation** - Automatic project completion percentage
- **Task Completion** - Simple checkbox to mark tasks done
- **Form Validation** - Both client and server-side validation

## Quick Start

The fastest way to get started:

```bash
./quickstart.sh
```

This script will:
1. Create virtual environment
2. Install dependencies
3. Set up database
4. Initialize with sample data
5. Start the application

**Sample Login:**
- Username: `testuser`
- Password: `password123`

## Manual Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Set up PostgreSQL database:

```bash
# Create a PostgreSQL database
createdb project_management

# Or using psql:
psql -U postgres
CREATE DATABASE project_management;
\q
```

5. Initialize the database:

```bash
# Initialize database tables only
python init_db.py

# Or initialize with sample data for testing
python init_db.py --with-data
```

6. Run the application:

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions.

**Quick Test:**
1. Login with sample data: `testuser` / `password123`
2. Explore the sample project with 3 tasks
3. Try completing tasks (note the dependency order)
4. Create your own projects and tasks
5. Test circular dependency prevention

## Documentation

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Complete testing instructions
- [VALIDATION.md](VALIDATION.md) - Validation rules and security features

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Frontend:** HTML, CSS, Jinja2 templates
- **Authentication:** Flask-Login with Werkzeug password hashing
- **Forms:** HTML5 validation + server-side validation

## Project Structure

```
.
├── run.py                 # Application entry point
├── config.py              # Configuration settings
├── models.py              # Database models
├── auth.py                # Authentication routes
├── projects.py            # Project CRUD routes
├── tasks.py               # Task CRUD routes
├── init_db.py             # Database initialization
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── view_project.html
│   └── ...
├── static/
│   └── css/
│       └── style.css      # Application styles
└── requirements.txt       # Python dependencies
```

## Architecture

**3-Tier Architecture:**
1. **Presentation Layer** - HTML templates with Jinja2
2. **Application Layer** - Flask routes and business logic
3. **Data Layer** - SQLAlchemy models and PostgreSQL

**Database Schema:**
- `User` - User accounts
- `Project` - Projects owned by users
- `Task` - Tasks within projects
- `task_dependencies` - Many-to-many task relationships

## Key Features Detail

### Task Dependencies
- Tasks can depend on other tasks in the same project
- Dependency validation ensures tasks are completed in order
- Circular dependency detection prevents A→B→C→A cycles
- Cannot delete tasks that others depend on

### Progress Calculation
- Automatically calculated from completed vs total tasks
- Updates in real-time when tasks are completed
- Displayed as percentage on dashboard and project view

### Security
- Password hashing with Werkzeug (PBKDF2)
- Flask-Login session management
- User authorization on all operations
- CSRF protection via POST forms
- No SQL injection (parameterized queries)

## Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run in debug mode (default)
python run.py

# Check logs (production mode only)
tail -f logs/app.log
```

## Future Enhancements

Potential improvements for the future:
- User profile management
- Project sharing and collaboration
- Task assignments to team members
- Due date notifications
- Task comments and attachments
- Export projects to PDF/Excel
- REST API for mobile apps
- Real-time updates with WebSockets

## License

This project is for educational purposes.
