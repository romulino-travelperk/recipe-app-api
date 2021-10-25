from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_tags_unauthenticated_should_fail(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'en@email.com',
            'aPassword'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_only_tags_belonging_to_user(self):
        user2 = get_user_model().objects.create_user(
            'anotheruser@email.com',
            password='anotherPassword'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        payload = {'name': 'Tag Name'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_with_empty_name_should_fail(self):
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_tags_assigned_to_recipes(self):
        tag1 = Tag.objects.create(user=self.user, name="Tag1")
        tag2 = Tag.objects.create(user=self.user, name="Tag2")

        recipe = Recipe.objects.create(
            user=self.user,
            title='A recipe',
            time_in_minutes=10,
            price=5.0
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 'true'})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_get_assigned_unique_tags(self):
        tag1 = Tag.objects.create(user=self.user, name="Tag1")
        tag2 = Tag.objects.create(user=self.user, name="Tag2")

        recipe = Recipe.objects.create(
            user=self.user,
            title='A recipe',
            time_in_minutes=10,
            price=5.0
        )

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='A recipe',
            time_in_minutes=10,
            price=5.0
        )

        recipe.tags.add(tag1)
        recipe2.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 'true'})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertEqual(len(res.data), 1)
        self.assertNotIn(serializer2.data, res.data)
