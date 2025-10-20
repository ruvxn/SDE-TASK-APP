"""
Integration tests for authentication routes
"""
import pytest
from models import User


@pytest.mark.auth
@pytest.mark.integration
class TestAuthRoutes:
    """Test authentication routes"""

    def test_register_page_loads(self, client):
        """Test that register page loads successfully"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data

    def test_login_page_loads(self, client):
        """Test that login page loads successfully"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_user_registration(self, client, db_session):
        """Test user registration functionality"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200

        # Check user was created in database
        user = db_session.query(User).filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'

    def test_user_login(self, client, test_user):
        """Test user login functionality"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should redirect to dashboard after login
        assert b'Dashboard' in response.data or b'Project' in response.data

    def test_login_with_wrong_password(self, client, test_user):
        """Test login with incorrect password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should show error message
        assert b'Invalid' in response.data or b'incorrect' in response.data.lower()

    def test_login_with_nonexistent_user(self, client):
        """Test login with non-existent username"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_logout(self, authenticated_client):
        """Test user logout functionality"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page
        assert b'Login' in response.data

    def test_protected_route_requires_login(self, client):
        """Test that protected routes redirect to login"""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect
        assert '/login' in response.location

    def test_duplicate_username_registration(self, client, test_user):
        """Test that duplicate usernames are rejected"""
        response = client.post('/register', data={
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        # Should show error or stay on registration page
        assert b'exists' in response.data.lower() or b'already' in response.data.lower() or b'Register' in response.data

    def test_password_mismatch_registration(self, client):
        """Test registration with mismatched passwords"""
        response = client.post('/register', data={
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password': 'password123',
            'confirm_password': 'different'
        }, follow_redirects=True)

        # Should show error or stay on registration page
        assert response.status_code == 200
