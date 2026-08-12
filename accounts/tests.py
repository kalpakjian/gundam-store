from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile


class UserModelTests(TestCase):
    """Test UserProfile signal creation."""

    def test_user_profile_auto_created(self):
        """UserProfile is automatically created when a User is created."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_user_profile_str(self):
        """UserProfile string representation."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(str(profile), "testuser")


class AuthViewTests(TestCase):
    """Test authentication views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
        )

    def test_login_get(self):
        """Login page returns 200."""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_success_non_ajax(self):
        """Non-AJAX login redirects to home on success."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_login_failure_non_ajax(self):
        """Non-AJAX login with wrong password shows error."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)

    def test_login_success_ajax(self):
        """AJAX login returns JSON success."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

    def test_login_failure_ajax(self):
        """AJAX login with wrong password returns JSON error."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "wrongpass"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])

    def test_register_get(self):
        """Register page returns 200."""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_success_non_ajax(self):
        """Non-AJAX registration creates user and redirects."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch(self):
        """Registration with mismatched passwords fails."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "password1": "ComplexPass123!",
                "password2": "DifferentPass456!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_logout_post(self):
        """POST logout redirects to home."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)

    def test_logout_get_redirects(self):
        """GET logout redirects to home."""
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)

