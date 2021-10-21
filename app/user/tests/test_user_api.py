from unittest import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            'email': 'an@email.com',
            'password': 'aPassword',
            'name': 'User Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


def test_create_an_user_that_already_exists_should_fail(self):
    payload = {'email': 'test@email.com', 'password': 'aPassword', 'name': 'A Name'}
    create_user(**payload)

    res = self.client.post(CREATE_USER_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


def test_password_must_be_more_than_5_characters(self):
    payload = {'email': 'some@email.com', 'password': 'pwd', 'name': 'A Name'}
    res = self.client.post(CREATE_USER_URL, payload)

    self.AssertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    user_exists = get_user_model().objects.filter(
        email=payload['email']
    ).exists
    self.assertFalse(user_exists)
