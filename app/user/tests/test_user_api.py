from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            'email': 'valid@email.com',
            'password': 'aPassword',
            'name': 'User Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertNotIn('password', res.data)
        self.assertTrue(user.check_password(payload['password']))

    def test_create_an_user_that_already_exists_should_fail(self):
        payload = {
            'email': 'test@email.com',
            'password': 'aPassword',
            'username': 'User Name'
        }
        create_user(email='test@email.com', password='aPassword')

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_must_be_more_than_5_characters(self):
        payload = {
            'email': 'some@email.com',
            'password': 'pwd',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        payload = {
            'username': 'an@email.com',
            'password': 'aPassword',
        }
        create_user(email='an@email.com', password='aPassword')
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_user_with_wrongPassword_fails(self):
        create_user(email='an@email.com',
                    password='correctPassword',
                    name='User Name')
        payload = {
            'username': 'an@email.com',
            'password': 'wrongPassword'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_non_existing_user_should_fail(self):
        payload = {
            'username': 'another@email.com',
            'password': 'goodPassword'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
