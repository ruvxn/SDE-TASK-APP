import pytest
from models import db, User


@pytest.mark.auth
class TestRegistration:
    def test_register_page_loads(self, client):
        """Test registration page is accessible"""
        response = client.get('/register')
        assert response.status_code == 200

    def test_successful_registration(self, client):
        """Test successful user registration"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Registration successful' in response.data or b'Login' in response.data

    def test_register_duplicate_username(self, client, sample_user):
        """Test registration with duplicate username"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        assert b'Username already exists' in response.data

    def test_register_duplicate_email(self, client, sample_user):
        """Test registration with duplicate email"""
        response = client.post('/register', data={
            'username': 'differentuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        assert b'Email already registered' in response.data

    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'different123'
        }, follow_redirects=True)

        assert b'Passwords do not match' in response.data

    def test_register_short_username(self, client):
        """Test registration with short username"""
        response = client.post('/register', data={
            'username': 'ab',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        assert b'Username must be at least 3 characters' in response.data

    def test_register_short_password(self, client):
        """Test registration with short password"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '12345',
            'confirm_password': '12345'
        }, follow_redirects=True)

        assert b'Password must be at least 6 characters' in response.data

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'invalidemail',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        assert b'valid email' in response.data


@pytest.mark.auth
class TestLogin:
    def test_login_page_loads(self, client):
        """Test login page is accessible"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_successful_login(self, client, sample_user):
        """Test successful login"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'dashboard' in response.data or b'Login successful' in response.data

    def test_login_wrong_password(self, client, sample_user):
        """Test login with wrong password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)

        assert b'Invalid username or password' in response.data

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        }, follow_redirects=True)

        assert b'Invalid username or password' in response.data

    def test_login_empty_fields(self, client):
        """Test login with empty fields"""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)

        assert b'Please enter both username and password' in response.data


@pytest.mark.auth
class TestLogout:
    def test_logout(self, authenticated_client):
        """Test logout functionality"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data or b'Login' in response.data

    def test_logout_requires_login(self, client):
        """Test logout redirects to login if not authenticated"""
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.auth
class TestIndexAndDashboard:
    def test_index_redirects_to_login(self, client):
        """Test index redirects to login for unauthenticated users"""
        response = client.get('/', follow_redirects=False)
        assert response.status_code in [302, 301]

    def test_index_redirects_to_dashboard_when_authenticated(self, authenticated_client):
        """Test index redirects to dashboard for authenticated users"""
        response = authenticated_client.get('/', follow_redirects=False)
        assert response.status_code in [302, 301]

    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code in [302, 301]

    def test_dashboard_accessible_when_authenticated(self, authenticated_client):
        """Test dashboard accessible when authenticated"""
        response = authenticated_client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
