# SDE TASK LIST APP

A simple web-based project management application built with Flask and PostgreSQL.

## Features

- User authentication
- Project creation and management
- Task creation with dependencies
- Task status tracking
- Automatic progress calculation

## Setup

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

## Tech Stack

- Backend: Flask (Python)
- Database: PostgreSQL with SQLAlchemy ORM
- Frontend: HTML, CSS, Jinja2 templates
