from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import AppUser, Task, Subtask, CustomContact

# Create your tests here.
class AuthTests(TestCase):
    def setUp(self):
        # Erstelle einen Benutzer für Authentifizierungstests
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
    def test_register_user(self):
        # Test für das Registrieren eines neuen Benutzers
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
# GuestLogin
# POST

# Register
# POST

# Login
# POST

# Users
# GET

# CurrentUser
# GET

# Tasks
# POST
# GET
# PUT
# DELETE

# Subtasks
# POST
# GET
# PUT
# DELETE

# Contacts
# POST
# GET
# PUT
# DELETE