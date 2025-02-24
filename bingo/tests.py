from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Profile, Task, UserTask, Leaderboard
from .views import email_validation, get_client_ip

User = get_user_model()


class ProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="profileuser", email="profile@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user)
        Profile.objects.create(user=self.user)

    def test_update_user_profile(self):
        url = reverse('update_user_profile')
        data = {"username": "updateduser"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")

    def test_update_user_profile_with_picture(self):
        url = reverse('update_user_profile')
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {"profile_picture": image}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = Profile.objects.get(user=self.user)
        self.assertTrue(profile.profile_picture)

    def test_update_user_profile_empty_payload(self):
        url = reverse('update_user_profile')
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "profileuser")
        self.assertEqual(self.user.email, "profile@exeter.ac.uk")

    def test_update_user_profile_with_invalid_file(self):
        url = reverse('update_user_profile')
        fake_file = SimpleUploadedFile("test.txt", b"fake content", content_type="text/plain")
        data = {"profile_picture": fake_file}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class EmailValidationTests(TestCase):
    def test_email_validation_valid(self):
        self.assertTrue(email_validation("user@exeter.ac.uk"))

    def test_email_validation_valid_uppercase(self):
        self.assertTrue(email_validation("USER@EXETER.AC.UK"))

    def test_email_validation_invalid_domain(self):
        self.assertFalse(email_validation("user@gmail.com"))
        self.assertFalse(email_validation("user@domain.com"))

    def test_email_validation_invalid_format(self):
        invalid_emails = [
            "userexeter.ac.uk",
            "user@@exeter.ac.uk",
            "user@exeter",
            "user@exeter..ac.uk",
            "user@.ac.uk",
            "user@exetercom",
            " user@exeter.ac.uk",
            "user@exeter.ac.uk ",
            "user @exeter.ac.uk",
            ""
        ]
        for email in invalid_emails:
            self.assertFalse(email_validation(email), f"Email '{email}' should be invalid")


class ClientIPTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_client_ip_with_forwarded_for(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 192.168.1.2'
        self.assertEqual(get_client_ip(request), '192.168.1.1')

    def test_get_client_ip_without_forwarded_for(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        self.assertEqual(get_client_ip(request), '192.168.1.100')

    def test_get_client_ip_empty(self):
        request = self.factory.get('/')
        request.META.pop('REMOTE_ADDR', None)  # Remove any default assigned IP
        request.META.pop('HTTP_X_FORWARDED_FOR', None)  # Ensure no forwarded-for IP is set
        self.assertIsNone(get_client_ip(request))


class RegisterUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')

    def test_register_valid_user(self):
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

    def test_register_missing_fields(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        data = {
            "username": "newuser",
            "password": "password123",
            "passwordagain": "password456",
            "email": "newuser@exeter.ac.uk",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        data = {
            "username": "newuser",
            "password": "password123",
            "passwordagain": "password123",
            "email": "newuser@gmail.com",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_existing_user(self):
        User.objects.create_user(username="existinguser", email="existing@exeter.ac.uk", password="password123")
        data = {
            "username": "existinguser",
            "password": "password123",
            "passwordagain": "password123",
            "email": "existing@exeter.ac.uk",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_login_success(self):
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data.get("user"), "testuser")

    # ---------- Tasks Tests ----------
    def test_tasks(self):
        # Create an additional task.
        Task.objects.create(
            id=2,
            description="Task 2",
            points=5
        )
        response = self.client.get('/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # Expect at least one task to be present.
        self.assertGreaterEqual(len(response.data), 1)

    # ---------- Complete Task Tests ----------
    def test_complete_task_success(self):
        self.client.force_authenticate(user=self.user)
        # Create a new task for completion.
        new_task = Task.objects.create(
            id=3,
            description="New Task",
            points=20
        )
        response = self.client.post('/complete_task/', {"task_id": new_task.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("points", response.data)
        # Verify that leaderboard points are updated.
        self.leaderboard.refresh_from_db()
        self.assertEqual(self.leaderboard.points, new_task.points)

    def test_complete_task_already_completed(self):
        self.client.force_authenticate(user=self.user)
        # First attempt: complete the task.
        response1 = self.client.post('/complete_task/', {"task_id": self.task.id})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Second attempt: should return error.
        response2 = self.client.post('/complete_task/', {"task_id": self.task.id})
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Task already completed", response2.data.get("message", ""))

    def test_complete_task_missing_task_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/complete_task/', {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_complete_task_nonexistent_task(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/complete_task/', {"task_id": 9999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_complete_task_auth_required(self):
        # Ensure endpoint is protected.
        self.client.force_authenticate(user=None)
        response = self.client.post('/complete_task/', {"task_id": self.task.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- Leaderboard Tests ----------
    def test_leaderboard_order(self):
        # Create another user with higher points.
        user2 = User.objects.create_user(
            username="user2",
            password="password2",
            email="user2@exeter.ac.uk"
        )
        Leaderboard.objects.create(user=user2, points=50)
        response = self.client.get('/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        if len(response.data) >= 2:
            # The user with higher points (user2) should appear first.
            self.assertEqual(response.data[0]["user"], user2.username)

    # ---------- Get User Profile Tests ----------
    def test_get_user_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        # Create a completed task and set leaderboard points.
        from .models import UserTask  # import here if not imported at the top
        UserTask.objects.create(user=self.user, task=self.task, completed=True)
        self.leaderboard.points = 10
        self.leaderboard.save()
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["total_points"], 10)
        self.assertEqual(response.data["completed_tasks"], 1)
        self.assertEqual(response.data["leaderboard_rank"], user_rank(10))

    def test_get_user_profile_auth_required(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- User Rank Tests ----------
    def test_user_rank_beginner(self):
        self.assertEqual(user_rank(10), "Beginner")

    def test_user_rank_intermediate(self):
        self.assertEqual(user_rank(100), "Intermediate")

    def test_user_rank_expert(self):
        self.assertEqual(user_rank(1300), "Expert")

    # ---------- Update User Profile Tests ----------
    def test_update_user_profile_without_picture(self):
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(description="Test Task", points=10)

    def test_fetch_tasks(self):
        url = reverse('tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_fetch_tasks_empty(self):
        Task.objects.all().delete()
        url = reverse('tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_fetch_tasks_structure(self):
        url = reverse('tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Profile updated successfully")
        # Refresh the user from the database.
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, new_username)
        self.assertEqual(self.user.email, new_email)

    def test_update_user_profile_with_picture(self):
        self.client.force_authenticate(user=self.user)
        new_username = "updatedwithpic"
        new_email = "updatedwithpic@example.com"
        # Create a dummy image file.
        image_content = b'\xff\xd8\xff\xe0\x00\x10JFIF'  # Minimal JPEG header bytes.
        image = SimpleUploadedFile("test_image.jpg", image_content, content_type="image/jpeg")
        data = {"username": new_username, "email": new_email, "profile_picture": image}
        response = self.client.put('/user/update/', data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Profile updated successfully")
        # Refresh the user and profile from the database.
        self.user.refresh_from_db()
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(self.user.username, new_username)
        self.assertEqual(self.user.email, new_email)
        # Check that a profile picture has been saved.
        self.assertTrue(profile.profile_picture)
