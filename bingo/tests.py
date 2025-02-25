# ============================
# Django Test Suite for API and Models
# Run Test: python manage.py test
# ============================

# Import necessary modules for testing
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APIClient

from unittest.mock import patch, mock_open, MagicMock

# Import models and views for testing
from bingo.models import Profile, Task, UserTask, Leaderboard
from bingo.views import user_rank, load_initial_tasks, login_user, tasks, get_user_profile, check_developer_role

import os
import json

# Retrieve the custom User model
User = get_user_model()


# ============================
# Load Initial Tasks Tests
# ============================

class LoadInitialTasksTestCase(TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='[{"pk": 2, "fields": {"description": "New Task", "points": 15, "requires_upload": false, "requires_scan": true}}]')
    @patch("os.path.join", return_value="mocked_path/initial_data.json")
    @patch("bingo.models.Task.objects.exists", return_value=False)
    @patch("bingo.models.Task.objects.create")
    def test_load_initial_tasks(self, mock_create, mock_exists, mock_path, mock_file):
        """Test loading initial tasks when no tasks exist"""
        load_initial_tasks()
        mock_create.assert_called_once_with(
            id=2,
            description="New Task",
            points=15,
            requires_upload=False,
            requires_scan=True
        )
        self.assertTrue(mock_create.called)

    @patch("builtins.open", new_callable=mock_open, read_data='[]')
    @patch("os.path.join", return_value="mocked_path/initial_data.json")
    @patch("bingo.models.Task.objects.exists", return_value=False)
    @patch("bingo.models.Task.objects.create")
    def test_load_initial_tasks_empty_file(self, mock_create, mock_exists, mock_path, mock_file):
        """Test loading initial tasks when JSON file is empty"""
        load_initial_tasks()
        mock_create.assert_not_called()

    @patch("os.path.join", return_value="mocked_path/initial_data.json")
    @patch("bingo.models.Task.objects.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_load_initial_tasks_already_exists(self, mock_file, mock_exists, mock_path):
        """Test loading initial tasks when tasks already exist"""
        load_initial_tasks()
        mock_file.assert_not_called()


# ============================
# User Profile Tests
# ============================

class ProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="profileuser", email="profile@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user)
        Profile.objects.create(user=self.user)

    def test_update_user_profile(self):
        """Test updating the user's username."""
        url = reverse('update_user_profile')
        data = {"username": "updateduser"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_update_user_profile_with_picture(self):
        """Test updating the user's profile picture."""
        url = reverse('update_user_profile')
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {"profile_picture": image}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = Profile.objects.get(user=self.user)
        self.assertTrue(profile.profile_picture)

    def test_update_user_profile_unsupported_picture_format(self):
        """Test updating the profile with an unsupported image format."""
        url = reverse('update_user_profile')
        unsupported_image = SimpleUploadedFile("test.gif", b"file_content", content_type="image/gif")
        data = {"profile_picture": unsupported_image}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# ============================
# User Registration Tests
# ============================

class RegisterUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')

    def test_register_valid_user(self):
        """Test registering a new user successfully."""
        data = {
            "username": "newuser",
            "password": "password123",
            "passwordagain": "password123",
            "email": "newuser@exeter.ac.uk",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch(self):
        """Test registration fails if passwords do not match."""
        data = {
            "username": "newuser",
            "password": "password123",
            "passwordagain": "password456",
            "email": "newuser@exeter.ac.uk",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_without_gdpr_consent(self):
        """Test registering a user without GDPR consent."""
        data = {
            "username": "newuser",
            "password": "password123",
            "passwordagain": "password123",
            "email": "newuser@example.com",
            "gdprConsent": False
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# ============================
# User Login Tests
# ============================

class LoginUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')

    def test_login_user_success(self):
        """Test logging in with correct credentials."""
        response = self.client.post(reverse('login_user'), {"username": "testuser", "password": "password123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_user_invalid_credentials(self):
        """Test logging in with incorrect password."""
        response = self.client.post(reverse('login_user'), {"username": "testuser", "password": "wrongpassword"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "Invalid username or password")

    def test_login_user_missing_fields(self):
        """Test logging in with missing fields."""
        response = self.client.post(reverse('login_user'), {"username": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "Username and password are required.")

    def test_login_user_nonexistent_username(self):
        """Test logging in with a username that does not exist."""
        response = self.client.post(reverse('login_user'), {"username": "nonexistent", "password": "password123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "Invalid username or password")

    def test_login_user_blank_password(self):
        """Test logging in with a blank password."""
        response = self.client.post(reverse('login_user'), {"username": "testuser", "password": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "Username and password are required.")

    def test_login_user_case_sensitivity(self):
        """Test login with different case in username."""
        response = self.client.post(reverse('login_user'), {"username": "TESTUSER", "password": "password123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "Invalid username or password")

# ============================
# Task Tests
# ============================

class TasksTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.task = Task.objects.create(id=1, description='Test Task', points=10, requires_upload=False, requires_scan=False)

    @patch("bingo.views.load_initial_tasks", autospec=True)
    def test_tasks_retrieval(self, mock_load_initial_tasks):
        """Test retrieving tasks and ensuring task preloading is called."""
        mock_load_initial_tasks.return_value = None  # Ensure function is patched properly
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)
        self.assertTrue(mock_load_initial_tasks.called)  # Ensure it was called at least once

    @patch("bingo.views.load_initial_tasks", autospec=True)
    def test_tasks_retrieval_no_tasks(self, mock_load_initial_tasks):
        """Test retrieving tasks when no tasks exist in the database."""
        Task.objects.all().delete()
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    @patch("bingo.views.load_initial_tasks", autospec=True)
    def test_tasks_retrieval_error_handling(self, mock_load_initial_tasks):
        """Test error handling when an exception occurs in task retrieval."""
        mock_load_initial_tasks.side_effect = Exception("Task loading error")
        with self.assertRaises(Exception) as context:
            self.client.get(reverse('tasks'))
        self.assertEqual(str(context.exception), "Task loading error")

# ============================
# Task Completion Tests
# ============================

class CompleteTaskTests(TestCase):
    """
    Tests for completing tasks and updating leaderboard scores.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="taskuser", email="task@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(description="Test Task", points=10)
        self.leaderboard = Leaderboard.objects.create(user=self.user, points=0)

    def test_complete_task_success(self):
        """Test successfully completing a task."""
        url = reverse('complete_task')
        data = {"task_id": self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Task completed!", response.data["message"])
        self.leaderboard.refresh_from_db()
        self.assertEqual(self.leaderboard.points, self.task.points)

# ============================
# Leaderboard Tests
# ============================

class LeaderboardTests(TestCase):
    """
    Tests for retrieving and ordering leaderboard entries.
    """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="leaderuser1", email="leader1@exeter.ac.uk", password="testpass")
        self.user2 = User.objects.create_user(username="leaderuser2", email="leader2@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user1)
        Leaderboard.objects.create(user=self.user1, points=100)
        Leaderboard.objects.create(user=self.user2, points=200)

    def test_leaderboard_ordering(self):
        """Test if the leaderboard is sorted correctly."""
        url = reverse('leaderboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data[0]["points"], response.data[1]["points"])

# ============================
# User Rank Tests
# ============================

class UserRankTests(TestCase):
    """
    Tests the ranking system based on user points.
    """
    def test_user_rank_beginner(self):
        """Test that users with 0-49 points are ranked as 'Beginner'."""
        self.assertEqual(user_rank(10), "Beginner")
        self.assertEqual(user_rank(0), "Beginner")

    def test_user_rank_intermediate(self):
        """Test that users with 50-1250 points are ranked as 'Intermediate'."""
        self.assertEqual(user_rank(100), "Intermediate")

    def test_user_rank_expert(self):
        """Test that users with more than 1250 points are ranked as 'Expert'."""
        self.assertEqual(user_rank(1300), "Expert")
