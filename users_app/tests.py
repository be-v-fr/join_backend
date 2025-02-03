import os
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from .models import AccountActivation, AccountActivationTokenGenerator, PasswordReset
from datetime import timedelta

os.environ.setdefault('FRONTEND_BASE_URL', 'http://localhost:4200/')

class AuthTests(APITestCase):
    """
    Authentication tests class testing user registration and login.
    """    
    def setUp(self):
        """
        Creates a user and an associated authentication token.
        """
        self.user = User.objects.create_user(username='testuser', email='testemail@email.com', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        
    def test_login_ok(self):
        """
        Tests successful login with correct credentials.
        
        Asserts:
            - 200 OK status.
            - Absence of username in response data.
            - Presence of required fields in response data.
        """
        data = {
            'email': self.user.email,
            'password': 'testpassword',
        }
        url = reverse('login')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('username', response.data)
        for key in ('token', 'email', 'user_id'):
            self.assertIn(key, response.data)
            
    def test_login_inactive_bad_request(self):
        """
        Tests login with inactive account.
        
        Asserts:
            - 400 Bad request status.
        """
        data = {
            'email': self.user.email,
            'password': 'testpassword',
        }
        self.user.is_active = False
        self.user.save()
        url = reverse('login')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_false_password_bad_request(self):
        """
        Tests login with incorrect password.
        
        Asserts:
            400 Bad Request status.
        """
        data = {
            'email': self.user.email,
            'password': 'wrongpassword',
        }
        url = reverse('login')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_not_registered_bad_request(self):
        """
        Tests login with incorrect password.
        
        Asserts:
            400 Bad Request status.
        """
        data = {
            'email': 'doesnotexist@mail.com',
            'password': 'randompassword',
        }
        url = reverse('login')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_signup_ok(self):
        """
        Tests successful signup with valid credentials.
        
        Asserts:
            - 201 Created status.
            - Created user is inactive.
            - Account activation token was created.
            - Username of new user is "User" plus primary key.
            - Absence of any token or user data in response.
        """
        data = {
            'email': 'seconduser@mail.com',
            'password': 'testPassword123',
        }
        url = reverse('signup')
        response = self.client.post(url, data, format='json')
        created_user = User.objects.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(created_user.is_active)
        self.assertTrue(AccountActivation.objects.filter(user=created_user).exists())
        self.assertEqual(created_user.username, 'User' + str(created_user.pk))
        for key in ('token', 'username', 'email', 'user_id'):
            self.assertNotIn(key, response.data)
        
        
    def test_signup_passwords_email_exists_bad_request(self):
        """
        Tests signup with non-matching passwords.
        
        Asserts:
            - 400 Bad request status.
        """
        data = {
            'email': self.user.email,
            'password': 'testPassword123',
        }
        url = reverse('signup')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
class AccountActivationTests(APITestCase):
    """
    Account activation test class testing account activation after user signup.
    """
    def setUp(self):
        """
        Setup method extending authentication setup by setting user activity and generating activation objects.
        """
        AuthTests.setUp(self)
        self.user.is_active = False
        self.user.save()
        self.activation_token = AccountActivationTokenGenerator().make_token(self.user)
        self.activation_obj = AccountActivation.objects.create(user=self.user, token=self.activation_token)
        
    def test_activate_ok(self):
        """
        Tests successful account activation, using an existing token.
        
        Asserts:
            - 200 OK status.
            - AccountActivation instance (containing the token) was deleted.
        """
        data = {
            'token': self.activation_token,
        }
        url = reverse('activate-account')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(AccountActivation.objects.filter(user=self.user).exists())
    
    def test_activate_double_token_ok(self):
        """
        Tests successful account activation, using a double existing token.
        
        Asserts:
            - 200 OK status.
            - AccountActivation instance (containing the token) was deleted.
        """
        self.scnd_activation_obj = AccountActivation.objects.create(user=self.user, token=self.activation_token + 'a')        
        data = {
            'token': self.activation_token,
        }
        url = reverse('activate-account')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(AccountActivation.objects.filter(user=self.user).exists())
        
    def test_activate_invalid_token_bad_request(self):
        """
        Tests failing account activation, using an invalid token.
        
        Asserts:
            - 400 Bad request status.
            - "token" key is in response.
        """
        data = {
            'token': '123456789abcdefg',
        }
        url = reverse('activate-account')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        
    def test_activate_expired_token_bad_request(self):
        """
        Tests failing account activation, using an expired token.
        
        Asserts:
            - 400 Bad request status.
            - "token" key is in response.
            - Token was deleted.
        """
        self.activation_obj.created_at -= timedelta(hours=25)
        self.activation_obj.save()
        data = {
            'token': self.activation_token,
        }
        url = reverse('activate-account')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        self.assertFalse(AccountActivation.objects.filter(user=self.user).exists())

class UserTests(APITestCase):
    """
    User test class testing user profile access.
    """
    def setUp(self):
        """
        Setup method extending authentication setup by logging in the user.
        """  
        AuthTests.setUp(self=self)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
      
    def test_get_user_ok(self):
        """
        Tests user retrieval by token.
        
        Asserts:
            - 200 OK status.
            - Username and email are not in response.
            - Required fields (ID only) is in response.
        """
        url = reverse('user')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in ('username', 'email'):
            self.assertNotIn(key, response.data)
        self.assertIn('id', response.data)
            
    def test_get_user_invalid_token(self):
        """
        Tests failing user retrieval by invalid token.
        
        Asserts:
            - 401 unauthorized status.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'invalidtokenkey')
        url = reverse('user')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_user_missing_token(self):
        """
        Tests failing user retrieval without any token.
        
        Asserts:
            - 401 unauthorized status.
        """
        self.client.logout()
        url = reverse('user')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PasswordResetTests(APITestCase):
    """
    Password reset test class testing password resetting.
    """
    def setUp(self):
        """
        Setup method extending authentication setup by generating password reset objects.
        """  
        AuthTests.setUp(self)
        self.pw_reset_token = PasswordResetTokenGenerator().make_token(self.user)
        self.pw_reset_obj = PasswordReset.objects.create(user=self.user, token=self.pw_reset_token)
        
    def test_request_ok(self):
        """
        Tests successful password reset request, creating a new token and replacing an existing one.
        
        Asserts:
            - 200 OK status.
            - Previous PasswordReset instance (containing the token) was deleted.
        """
        data = {
            'email': self.user.email,
        }
        url = reverse('request-pw-reset')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(PasswordReset.objects.filter(user=self.user)), 1)
        
    def test_request_unregistered_email_ok(self):
        """
        Tests failing password reset request due to an unregistered email address.
        For security reasons, the 200 OK status is sent nonetheless.
        
        Asserts:
            - 200 OK status.
            - Length of PasswordReset queryset is the same as before, i.e. no PasswordReset object was created.
        """
        queryset_count_before = PasswordReset.objects.count()
        data = {
            'email': 'nonexisting_user@mail.com',
        }
        url = reverse('request-pw-reset')
        response = self.client.post(url, data, format='json')
        queryset_count_after = PasswordReset.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(queryset_count_before, queryset_count_after)
        
    def test_request_invalid_email_bad_request(self):
        """
        Tests failing password reset request due to an invalid email address.
        
        Asserts:
            - 400 Bad request status.
            - "email" key is in response.
        """
        data = {
            'email': 'invalid@mail',
        }
        url = reverse('request-pw-reset')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_perform_reset_ok(self):
        """
        Tests successful password reset, using an existing token.
        
        Asserts:
            - 200 OK status.
            - PasswordReset instance (containing the token) was deleted.
        """
        data = {
            'token': self.pw_reset_token,
            'new_password': 'asd123asd123',
        }
        url = reverse('perform-pw-reset')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PasswordReset.objects.filter(user=self.user).exists())
        
    def test_perform_reset_invalid_token_bad_request(self):
        """
        Tests failing password reset, using an invalid token.
        
        Asserts:
            - 400 Bad request status.
            - "token" key is in response.
        """
        data = {
            'token': '123456789abcdefg',
            'new_password': 'asd123asd123',
        }
        url = reverse('perform-pw-reset')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        
    def test_perform_reset_expired_token_bad_request(self):
        """
        Tests failing password reset, using an expired token.
        
        Asserts:
            - 400 Bad request status.
            - "token" key is in response.
            - Token was deleted.
        """
        self.pw_reset_obj.created_at -= timedelta(hours=25)
        self.pw_reset_obj.save()
        data = {
            'token': self.pw_reset_token,
            'new_password': 'asd123asd123',
        }
        url = reverse('perform-pw-reset')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)
        self.assertFalse(PasswordReset.objects.filter(user=self.user).exists())
        
    def test_perform_reset_weak_pw_bad_request(self):
        """
        Tests failing password reset, using an invalid password.
        
        Asserts:
            - 400 Bad request status.
            - "new_password" key is in response.
        """
        data = {
            'token': self.pw_reset_token,
            'new_password': 'asd123',
        }
        url = reverse('perform-pw-reset')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)