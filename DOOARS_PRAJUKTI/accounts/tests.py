"""
Tests for Accounts App
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=User.Role.TEAM_MEMBER
        )
    
    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(self.user.role, User.Role.TEAM_MEMBER)
    
    def test_user_str(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'testuser')
    
    def test_is_super_admin(self):
        """Test is_super_admin property"""
        self.assertFalse(self.user.is_super_admin)
        
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role=User.Role.SUPER_ADMIN
        )
        self.assertTrue(admin.is_super_admin)
    
    def test_is_manager(self):
        """Test is_manager property"""
        self.assertFalse(self.user.is_manager)
        
        manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='managerpass123',
            role=User.Role.MANAGER
        )
        self.assertTrue(manager.is_manager)
    
    def test_is_team_member(self):
        """Test is_team_member property"""
        self.assertTrue(self.user.is_team_member)


class SignUpViewTest(TestCase):
    """Test cases for signup view"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.signup_url = reverse('signup')
    
    def test_signup_page_loads(self):
        """Test signup page loads successfully"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_signup_with_valid_data(self):
        """Test signup with valid data"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'role': User.Role.TEAM_MEMBER,
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        response = self.client.post(self.signup_url, data)
        
        # Should redirect after successful signup
        self.assertEqual(response.status_code, 302)
        
        # User should be created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # User should be logged in
        user = User.objects.get(username='newuser')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
    
    def test_signup_with_duplicate_username(self):
        """Test signup with duplicate username"""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='pass123'
        )
        
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'role': User.Role.TEAM_MEMBER,
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        response = self.client.post(self.signup_url, data)
        
        # Should not create user
        self.assertEqual(User.objects.filter(email='new@example.com').count(), 0)
        
        # Should show error
        self.assertFormError(
            response, 'form', 'username',
            'A user with that username already exists.'
        )
    
    def test_signup_with_duplicate_email(self):
        """Test signup with duplicate email"""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='pass123'
        )
        
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'role': User.Role.TEAM_MEMBER,
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        response = self.client.post(self.signup_url, data)
        
        # Should not create user
        self.assertEqual(User.objects.filter(username='newuser').count(), 0)
        
        # Should show error
        self.assertFormError(
            response, 'form', 'email',
            'A user with that email already exists.'
        )
    
    def test_signup_with_password_mismatch(self):
        """Test signup with non-matching passwords"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'role': User.Role.TEAM_MEMBER,
            'password1': 'complexpass123',
            'password2': 'differentpass123',
        }
        response = self.client.post(self.signup_url, data)
        
        # Should not create user
        self.assertEqual(User.objects.filter(username='newuser').count(), 0)


class SignInViewTest(TestCase):
    """Test cases for signin view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.signin_url = reverse('signin')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=User.Role.TEAM_MEMBER
        )
    
    def test_signin_page_loads(self):
        """Test signin page loads successfully"""
        response = self.client.get(self.signin_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_signin_with_valid_credentials(self):
        """Test signin with valid credentials"""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(self.signin_url, data)
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # User should be logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
    
    def test_signin_with_invalid_credentials(self):
        """Test signin with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.signin_url, data)
        
        # Should not redirect
        self.assertEqual(response.status_code, 200)
        
        # User should not be logged in
        self.assertNotIn('_auth_user_id', self.client.session)
    
    def test_signin_redirects_authenticated_user(self):
        """Test signin redirects already authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.signin_url)
        
        # Should redirect
        self.assertEqual(response.status_code, 302)


class LogoutViewTest(TestCase):
    """Test cases for logout view"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_logout_redirects_unauthenticated_user(self):
        """Test logout redirects unauthenticated users"""
        response = self.client.get(self.logout_url)
        
        # Should redirect to login (because of @login_required)
        self.assertEqual(response.status_code, 302)
    
    def test_logout_authenticated_user(self):
        """Test logout for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.logout_url)
        
        # Should redirect after logout
        self.assertEqual(response.status_code, 302)
        
        # User should be logged out
        self.assertNotIn('_auth_user_id', self.client.session)


# Run tests with:
# python manage.py test accounts