from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_sample_user(email='some@email.com', password='apassword123'):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = 'email@domain.com'
        password = 'aPassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_normalized_domain_name(self):
        email = 'anotheremail@DomAin.com'
        password = 'aPassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())
        self.assertTrue(user.check_password(password))

    def test_new_user_with_invalid_email_raises_error(self):
        with self.assertRaises(ValueError):
            email = ''
            password = 'aPassword'
            get_user_model().objects.create_user(
                email=email,
                password=password
            )

    def test_create_new_super_user(self):
        user = get_user_model().objects.create_superuser(
            'address@domain.com', 'aPassword'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_string_representation(self):
        tag = models.Tag.objects.create(
            user=create_sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)
