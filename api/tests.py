from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import AppUser, Task, Subtask, CustomContact
from api.choices import TECHNICAL_TASK


class AuthTests(TestCase):
    """
    Test suite for authentication-related actions, including registration, login, and guest login.
    """
    def setUp(self):
        """
        Set up initial data for tests, creating a test user, app user, and token for authentication.
        """
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        
    def test_register_user(self):
        """
        Test the user registration process.
        """
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
    def test_login_user(self):
        """
        Test the login process for an existing user.
        """
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        
    def test_guest_login(self):
        """
        Test the guest login functionality, allowing anonymous users to log in.
        """
        url = reverse('login_guest')
        data = {'username': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        
class UsersTests(TestCase):
    """
    Test suite for actions related to user retrieval, including getting all users and the current user.
    """
    def setUp(self):
        """
        Set up initial data, including creating a test user, app user, and token.
        """
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        
    def test_users(self):
        """
        Test retrieving the list of all users.
        """
        url = reverse('users')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_users_current(self):
        """
        Test retrieving the current logged-in user.
        """
        url = reverse('users_current')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TaskTests(TestCase):
    """
    Test suite for actions related to tasks, including retrieving, creating, updating, and deleting tasks.
    """
    def setUp(self):
        """
        Set up initial data, creating a test user, app user, task, subtask, and token.
        """
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.task = Task.objects.create(title="Task 1")
        self.subtask = Subtask.objects.create(name="Subtask 1", task=self.task)


    def test_get_tasks(self):
        """
        Test retrieving a list of all tasks.
        """
        url = reverse('tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        
    def test_create_task_with_subtasks(self):
        """
        Test creating a task along with its subtasks.
        """
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
        """
        Test updating an existing task and its associated subtasks.
        """
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
        """
        Test deleting an existing task.
        """
        url = reverse('task', kwargs={'pk': self.task.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())


class SubtaskTests(TestCase):
    """
    Test suite for actions related to subtasks, including retrieving, creating, updating, and deleting subtasks.
    """
    def setUp(self):
        """
        Set up initial data, creating a test user, app user, task, subtask, and token.
        """
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.task = Task.objects.create(title="Task 1")
        self.subtask = Subtask.objects.create(name="Subtask 1", task=self.task)


    def test_get_subtasks(self):
        """
        Test retrieving a list of all subtasks.
        """
        url = reverse('subtasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_create_subtask(self):
        """
        Test creating a new subtask.
        """
        url = reverse('subtasks')
        data = {'name': 'New Subtask', 'task': self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_update_subtask(self):
        """
        Test updating an existing subtask.
        """
        url = reverse('subtask', kwargs={'pk': self.subtask.id})
        data = {'name': 'Updated Subtask', 'task': self.task.id}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subtask.refresh_from_db()
        self.assertEqual(self.subtask.name, 'Updated Subtask')


    def test_delete_subtask(self):
        """
        Test deleting an existing subtask.
        """
        url = reverse('subtask', kwargs={'pk': self.subtask.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subtask.objects.filter(id=self.subtask.id).exists())


class ContactTests(TestCase):
    """
    Test suite for actions related to contacts, including creating, retrieving, updating, and deleting contacts.
    """
    def setUp(self):
        """
        Set up initial data, including creating a test user, app user, and token.
        """
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.app_user = AppUser.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)


    def test_create_contact(self):
        """
        Test creating a new contact.
        """
        url = reverse('contacts')
        data = {'name': 'Contact 1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_get_contacts(self):
        """
        Test retrieving a list of all contacts.
        """
        CustomContact.objects.create(app_user=self.app_user, name='Contact 1')
        url = reverse('contacts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_update_contact(self):
        """
        Test updating an existing contact.
        """
        contact = CustomContact.objects.create(app_user=self.app_user, name='Contact 1')
        url = reverse('contact', kwargs={'pk': contact.id})
        data = {'name': 'Updated Contact'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact.refresh_from_db()
        self.assertEqual(contact.name, 'Updated Contact')


    def test_delete_contact(self):
        """
        Test deleting an existing contact.
        """
        contact = CustomContact.objects.create(app_user=self.app_user, name='Contact 1')
        url = reverse('contact', kwargs={'pk': contact.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomContact.objects.filter(id=contact.id).exists())