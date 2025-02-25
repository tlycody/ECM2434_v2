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

class RegisterUserTests(TestCase):
    """
    Tests for user registration.
    """
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
