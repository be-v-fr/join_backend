from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from users_app.models import AppUser
from .models import CustomContact

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
