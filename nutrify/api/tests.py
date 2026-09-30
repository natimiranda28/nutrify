from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from .models import Category, DietaryRestriction, Establishment, Product


class ApiTests(APITestCase):
    def setUp(self):
        self.celiac = DietaryRestriction.objects.create(
            name="Celíaca", slug="celiaquia"
        )
        self.diabetes = DietaryRestriction.objects.create(
            name="Diabetes", slug="diabetes"
        )
        self.ice_cream = Category.objects.create(name="Helado", slug="helado")
        self.pizzeria = Category.objects.create(name="Pizza", slug="pizza")
        self.place = Establishment.objects.create(
            name="Heladería Roma",
            slug="heladeria-roma",
            address="Calle 123",
            latitude=-34.6037,
            longitude=-58.3816,
        )
        self.product = Product.objects.create(
            establishment=self.place,
            category=self.ice_cream,
            name="Chocolate sin azúcar agregada",
        )
        self.product.declared_compatible_with.add(self.diabetes)

    def test_search_filters_products_by_all_requested_restrictions(self):
        response = self.client.get(
            "/api/establishments/search/",
            {"restrictions": "diabetes", "latitude": -34.604, "longitude": -58.382},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result["slug"], "heladeria-roma")
        self.assertEqual(result["products"][0]["name"], "Chocolate sin azúcar agregada")
        self.assertAlmostEqual(result["distance_km"], 0.04, delta=0.1)

    def test_search_excludes_product_missing_a_requested_declaration(self):
        response = self.client.get(
            "/api/establishments/search/",
            {"restrictions": "diabetes,celiaquia"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_search_rejects_unknown_restrictions(self):
        response = self.client.get(
            "/api/establishments/search/", {"restrictions": "unknown"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_requires_both_coordinates(self):
        response = self.client.get(
            "/api/establishments/search/", {"latitude": -34.6}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_creates_profile_and_jwt_login_works(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "usuario",
                "email": "user@example.com",
                "password": "UnaClaveSegura2026!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["restrictions"], [])
        token_response = self.client.post(
            "/api/auth/token/",
            {"username": "usuario", "password": "UnaClaveSegura2026!"},
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_response.data)

    def test_authenticated_user_can_update_profile_restrictions(self):
        user = self.client.post(
            "/api/auth/register/",
            {
                "username": "perfil",
                "email": "profile@example.com",
                "password": "UnaClaveSegura2026!",
            },
            format="json",
        )
        account = get_user_model().objects.get(pk=user.data["id"])
        self.client.force_authenticate(account)
        response = self.client.patch(
            "/api/profile/", {"restrictions": [self.diabetes.pk]}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["restrictions"], [self.diabetes.pk])
