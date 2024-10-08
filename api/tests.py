from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import AppUser, Task, Subtask, CustomContact
from api.choices import TECHNICAL_TASK

# Create your tests here.
class AuthTests(TestCase):
    
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        
    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
    def test_login_user(self):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        
    def test_guest_login(self):
        url = reverse('login_guest')
        data = {'username': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        
class UsersTests(TestCase):


    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        
    def test_users(self):
        url = reverse('users')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_users_current(self):
        url = reverse('users_current')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TaskTests(TestCase):


    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.task = Task.objects.create(title="Task 1")
        self.subtask = Subtask.objects.create(name="Subtask 1", task=self.task)


    def test_get_tasks(self):
        url = reverse('tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        
    def test_create_task_with_subtasks(self):
        url = reverse('tasks')
        data = {
            "title": "Task 2",
            "subtasks": [
                {"name": "Subtask A"},
                {"name": "Subtask B"}
            ],
            "description": "",
            "assigned_to": [1],
            "due": "2024-11-02",
            "category": "Technical Task",
            "prio": "Medium",
            "status": "To do"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
    def test_update_task(self):
        url = reverse('task', kwargs={'pk': self.task.id})
        data = {
            "id": self.task.id,
            "title": "Updated Task",
            "subtasks": [
                {
                    "id": self.subtask.id,
                    "name": "Subtask A",
                    "task": 1
                },
            ],
            "description": "",
            "assigned_to": [1],
            "due": "2024-11-02",
            "category": "Technical Task",
            "prio": "Medium",
            "status": "To do"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        
        
    def test_delete_task(self):
        url = reverse('task', kwargs={'pk': self.task.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())


class SubtaskTests(TestCase):
    
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.task = Task.objects.create(title="Task 1")
        self.subtask = Subtask.objects.create(name="Subtask 1", task=self.task)


    def test_get_subtasks(self):
        url = reverse('subtasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_create_subtask(self):
        url = reverse('subtasks')
        data = {'name': 'New Subtask', 'task': self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_update_subtask(self):
        url = reverse('subtask', kwargs={'pk': self.subtask.id})
        data = {'name': 'Updated Subtask', 'task': self.task.id}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subtask.refresh_from_db()
        self.assertEqual(self.subtask.name, 'Updated Subtask')


    def test_delete_subtask(self):
        url = reverse('subtask', kwargs={'pk': self.subtask.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subtask.objects.filter(id=self.subtask.id).exists())


class ContactTests(TestCase):


    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)


    def test_create_contact(self):
        url = reverse('contacts')
        data = {'name': 'Contact 1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_get_contacts(self):
        CustomContact.objects.create(app_user=self.app_user, name='Contact 1')
        url = reverse('contacts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_update_contact(self):
        contact = CustomContact.objects.create(app_user=self.app_user, name='Contact 1')
        url = reverse('contact', kwargs={'pk': contact.id})
        data = {'name': 'Updated Contact'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact.refresh_from_db()
        self.assertEqual(contact.name, 'Updated Contact')


    def test_delete_contact(self):
        contact = CustomContact.objects.create(app_user=self.app_user, name='Contact 1')
        url = reverse('contact', kwargs={'pk': contact.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomContact.objects.filter(id=contact.id).exists())