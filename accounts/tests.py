from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountsTests(TestCase):
    def test_signup_creates_user(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "ComplexPass123",
            "password2": "ComplexPass123",
        }
        response = self.client.post(reverse("accounts:signup"), payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_page_loads(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
