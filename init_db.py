from run import app
from models import db, User, Project, Task

def init_database():
    """initialise the database with tables"""
    with app.app_context():
        #BE CAREFUL WITH THIS!!!
        #THIS WILL DROP ALL THE TABLES
        db.drop_all()
        db.create_all()
        print("database tables created successfully!")

def seed_sample_data():
    """add sample data for testing (optional)"""
    with app.app_context():
        # create test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print(f"sample user created: {user.username}")

        #create sample project
        project = Project(
            name='Sample Project',
            description='This is a test project',
            user_id=user.id
        )
        db.session.add(project)
        db.session.commit()
        print(f"Sample project created: {project.name}")

        #create sample tasks
        task1 = Task(
            title='Setup development environment',
            description='Install required tools and dependencies',
            importance='high',
            project_id=project.id
        )
        task2 = Task(
            title='Design database schema',
            description='Create ER diagrams and define relationships',
            importance='high',
            project_id=project.id
        )
        task3 = Task(
            title='Implement user authentication',
            description='Build login and registration system',
            importance='medium',
            project_id=project.id
        )

        db.session.add_all([task1, task2, task3])
        db.session.commit()

        # Add dependency: task3 depends on task1 and task2
        task3.dependencies.append(task1)
        task3.dependencies.append(task2)
        db.session.commit()

        print(f"sample tasks created with dependencies")
        print("\nsample data added successfully!")
        print(f"login credentials - Username: testuser, Password: password123")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--with-data':
        init_database()
        seed_sample_data()
    else:
        init_database()
        print("\nrun 'python init_db.py --with-data' to add sample data")
