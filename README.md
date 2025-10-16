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

4. Run the application:

```bash
python run.py
```

## Tech Stack

- Backend: Flask (Python)
- Database: PostgreSQL with SQLAlchemy ORM
- Frontend: HTML, CSS, Jinja2 templates
