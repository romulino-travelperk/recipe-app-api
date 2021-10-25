import os.path
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailsSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def image_upload_url_for(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def recipe_detail_url_for(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_sample_tag(user, name='Default Tag'):
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name='Default Ingredient'):
    return Ingredient.objects.create(user=user, name=name)


def create_sample_recipe(user, **params):
    defaults = {
        'title': 'Default recipe title',
        'time_in_minutes': 10,
        'price': 10.0
    }
    defaults.update(**params)

    return Recipe.objects.create(user=user, **defaults)


class PublicTagsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_recipes_unauthenticated_should_fail(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'anUser@email.com', 'somePassword'
        )
        self.client.force_authenticate(self.user)

    def test_get_recipes(self):
        create_sample_recipe(user=self.user)
        create_sample_recipe(user=self.user)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_gets_only_recipes_belonging_to_user(self):
        another_user = get_user_model().objects.create_user(
            'yetanotheruser@email.com', 'anotherPassword'
        )
        create_sample_recipe(user=another_user)
        create_sample_recipe(user=another_user)
        create_sample_recipe(user=another_user)
        create_sample_recipe(user=self.user)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 1)

    def test_get_recipe_details(self):
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))

        recipe_url = recipe_detail_url_for(recipe.id)

        serializer = RecipeDetailsSerializer(recipe)

        res = self.client.get(recipe_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        payload = {
            'title': 'A recipe',
            'time_in_minutes': 10,
            'price': 5.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEquals(res.data['title'], payload['title'])
        self.assertEquals(int(res.data['time_in_minutes']),
                          int(payload['time_in_minutes']))
        self.assertEqual(float(res.data['price']),
                         float(payload['price']))

    def test_create_recipe_with_tags(self):
        tag1 = create_sample_tag(user=self.user, name='a Tag')
        tag2 = create_sample_tag(user=self.user, name='another Tag')

        payload = {
            'title': 'A recipe',
            'time_in_minutes': 10,
            'price': 20.00,
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEquals(res.data['title'], payload['title'])

        self.assertEquals(int(res.data['time_in_minutes']),
                          int(payload['time_in_minutes']))

        self.assertEqual(float(res.data['price']),
                         float(payload['price']))

        self.assertEquals(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ingredient1 = create_sample_ingredient(user=self.user,
                                               name='an ingredient')
        ingredient2 = create_sample_ingredient(user=self.user,
                                               name='another ingredient')

        payload = {
            'title': 'A recipe',
            'time_in_minutes': 10,
            'price': 20.00,
            'ingredients': [ingredient1.id, ingredient2.id]
        }

        res = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEquals(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

        self.assertEquals(res.data['title'], payload['title'])
        self.assertEquals(int(res.data['time_in_minutes']),
                          int(payload['time_in_minutes']))

        self.assertEqual(float(res.data['price']),
                         float(payload['price']))

    def test_create_recipe_with_ingredients_and_tags(self):
        ingredient1 = create_sample_ingredient(user=self.user,
                                               name='an ingredient')
        ingredient2 = create_sample_ingredient(user=self.user,
                                               name='another ingredient')
        ingredient3 = create_sample_ingredient(user=self.user,
                                               name='yet another ingredient')
        tag1 = create_sample_tag(user=self.user, name='a Tag')
        tag2 = create_sample_tag(user=self.user, name='another Tag')

        payload = {
            'title': 'A recipe',
            'time_in_minutes': 10,
            'price': 20.00,
            'ingredients': [ingredient1.id, ingredient2.id, ingredient3.id],
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        tags = recipe.tags.all()

        self.assertEquals(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

        self.assertEquals(ingredients.count(), 3)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
        self.assertIn(ingredient3, ingredients)

        self.assertEquals(res.data['title'], payload['title'])

        self.assertEquals(int(res.data['time_in_minutes']),
                          int(payload['time_in_minutes']))

        self.assertEqual(float(res.data['price']),
                         float(payload['price']))


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'an@email.com',
            'somePassword'
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        image_url = image_upload_url_for(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            res = self.client.post(image_url,
                                   {'image': image_file},
                                   format='multipart')

            self.recipe.refresh_from_db()

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn('image', res.data)
            self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_invalid_image_should_fail(self):
        image_url = image_upload_url_for(self.recipe.id)
        res = self.client.post(image_url,
                               {'image': 'NotAnImage'},
                               format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
