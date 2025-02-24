from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Profile, Task, UserTask, Leaderboard
from .views import email_validation, get_client_ip

User = get_user_model()


class ClientIPTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_client_ip_with_forwarded_for(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 192.168.1.2'
        self.assertEqual(get_client_ip(request), '192.168.1.1')

    def test_get_client_ip_with_single_forwarded_for(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.5'
        self.assertEqual(get_client_ip(request), '203.0.113.5')

    def test_get_client_ip_with_multiple_forwarded_for_spaces(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = ' 192.168.1.10 , 192.168.1.11 '
        self.assertEqual(get_client_ip(request).strip(), '192.168.1.10')

    def test_get_client_ip_without_forwarded_for(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        self.assertEqual(get_client_ip(request), '192.168.1.100')

    def test_get_client_ip_empty(self):
        request = self.factory.get('/')
        request.META.pop('REMOTE_ADDR', None)  # Remove any default assigned IP
        request.META.pop('HTTP_X_FORWARDED_FOR', None)  # Ensure no forwarded-for IP is set
        self.assertIsNone(get_client_ip(request))

    def test_get_client_ip_invalid_forwarded_for(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = 'invalid_ip'
        self.assertEqual(get_client_ip(request), 'invalid_ip')  # Function does not validate IP format

    def test_get_client_ip_malformed_forwarded_for(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = ' , , '
        self.assertEqual(get_client_ip(request).strip(), '')  # Should return an empty string after stripping spaces

    def test_get_client_ip_multiple_headers(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 192.168.1.2'
        request.META['REMOTE_ADDR'] = '203.0.113.5'
        self.assertEqual(get_client_ip(request), '192.168.1.1')

    def test_get_client_ip_remote_addr_overrides_empty_forwarded_for(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = ''
        request.META['REMOTE_ADDR'] = '203.0.113.5'
        self.assertEqual(get_client_ip(request), '203.0.113.5')


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

    def test_update_user_profile_with_existing_picture_replacement(self):
        url = reverse('update_user_profile')
        image1 = SimpleUploadedFile("image1.jpg", b"file_content1", content_type="image/jpeg")
        data1 = {"profile_picture": image1}
        self.client.put(url, data1, format='multipart')
        profile = Profile.objects.get(user=self.user)
        old_picture = profile.profile_picture.name

        image2 = SimpleUploadedFile("image2.jpg", b"file_content2", content_type="image/jpeg")
        data2 = {"profile_picture": image2}
        response = self.client.put(url, data2, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        new_picture = profile.profile_picture.name
        self.assertNotEqual(old_picture, new_picture)

    def test_update_user_profile_with_unsupported_file_type(self):
        url = reverse('update_user_profile')
        pdf_file = SimpleUploadedFile("document.pdf", b"%PDF-1.4 fake content", content_type="application/pdf")
        data = {"profile_picture": pdf_file}
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_update_user_profile_without_authentication(self):
        self.client.force_authenticate(user=None)
        url = reverse('update_user_profile')
        data = {"username": "newuser"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailValidationTests(TestCase):
    def test_email_validation_valid(self):
        self.assertTrue(email_validation("user@exeter.ac.uk"))

    def test_email_validation_valid_uppercase(self):
        self.assertTrue(email_validation("USER@EXETER.AC.UK"))

    def test_email_validation_valid_leading_trailing_spaces(self):
        self.assertTrue(email_validation(" user@exeter.ac.uk ".strip()))

    def test_email_validation_invalid_domain(self):
        self.assertFalse(email_validation("user@gmail.com"))
        self.assertFalse(email_validation("user@domain.com"))
        self.assertFalse(email_validation("user@exeter.com"))
        self.assertFalse(email_validation("user@exeter.edu"))
        self.assertFalse(email_validation("user@ac.exeter.uk"))
        self.assertFalse(email_validation("user@exeter.ac.co.uk"))

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
            "",
            "user@exeter..ac.uk",
            "@exeter.ac.uk",
            "user@exeter.ac.uk@extra.com",
            "user@exeter_ac.uk",
            "user@exeter/ac.uk",
            "user@exeter ac.uk",
            "user@exeter.ac.uk ",
            "user@exeter.ac.uk.",
            "user@-exeter.ac.uk",
            "user@exeter-.ac.uk",
            "user@exeter.ac.uk.",
            "user.@exeter.ac.uk",
            ".user@exeter.ac.uk"
        ]
        for email in invalid_emails:
            self.assertFalse(email_validation(email), f"Email '{email}' should be invalid")

    def test_email_validation_with_numeric_usernames(self):
        self.assertTrue(email_validation("12345@exeter.ac.uk"))
        self.assertFalse(email_validation("12345@exeter.com"))

    def test_email_validation_with_mixed_case(self):
        self.assertTrue(email_validation("User123@EXETER.ac.uk"))
        self.assertFalse(email_validation("User123@ExEtEr.Com"))


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

    def test_register_without_gdpr_consent(self):
        data = {
            "username": "newuser",
            "password": "password123",
            "passwordagain": "password123",
            "email": "newuser@exeter.ac.uk",
            "gdprConsent": False
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_numeric_username(self):
        data = {
            "username": "123456",
            "password": "password123",
            "passwordagain": "password123",
            "email": "newuser@exeter.ac.uk",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_email_case_insensitivity(self):
        data = {
            "username": "caseinsensitive",
            "password": "password123",
            "passwordagain": "password123",
            "email": "NewUser@ExEtEr.Ac.Uk",
            "gdprConsent": True
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="caseinsensitive").exists())


class LoginUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api_login')
        self.user = User.objects.create_user(username="testuser", email="test@exeter.ac.uk", password="testpass")

    def test_login_valid_user(self):
        data = {"username": "testuser", "password": "testpass"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_invalid_credentials(self):
        data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TasksTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="taskuser", email="task@exeter.ac.uk", password="testpass")
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
        if response.data:
            self.assertIn("description", response.data[0])
            self.assertIn("points", response.data[0])


class CompleteTaskTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="taskuser", email="task@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user)
        self.task = Task.objects.create(description="Test Task", points=10)
        self.leaderboard = Leaderboard.objects.create(user=self.user, points=0)

    def test_complete_task_success(self):
        url = reverse('complete_task')
        data = {"task_id": self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Task completed!", response.data["message"])
        self.leaderboard.refresh_from_db()
        self.assertEqual(self.leaderboard.points, self.task.points)

    def test_complete_task_already_completed(self):
        UserTask.objects.create(user=self.user, task=self.task, completed=True)
        url = reverse('complete_task')
        data = {"task_id": self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Task already completed!", response.data["message"])

    def test_complete_task_invalid_task(self):
        url = reverse('complete_task')
        data = {"task_id": 9999}  # Non-existent task ID
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_complete_task_without_authentication(self):
        self.client.force_authenticate(user=None)
        url = reverse('complete_task')
        data = {"task_id": self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_complete_task_updates_leaderboard(self):
        url = reverse('complete_task')
        data = {"task_id": self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.leaderboard.refresh_from_db()
        self.assertEqual(self.leaderboard.points, 10)

    def test_complete_task_creates_user_task_entry(self):
        url = reverse('complete_task')
        data = {"task_id": self.task.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserTask.objects.filter(user=self.user, task=self.task, completed=True).exists())


class LeaderboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="leaderuser", email="leader@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user)
        Leaderboard.objects.create(user=self.user, points=100)

    def test_leaderboard(self):
        url = reverse('leaderboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)


class UserProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="profileuser", email="profile@exeter.ac.uk", password="testpass")
        self.client.force_authenticate(user=self.user)
        Profile.objects.create(user=self.user)

    def test_get_user_profile(self):
        url = reverse('get_user_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("total_points", response.data)
        self.assertIn("completed_tasks", response.data)
        self.assertIn("leaderboard_rank", response.data)
        self.assertIn("profile_picture", response.data)


class UserRankTests(TestCase):
    def test_user_rank_beginner(self):
        from .views import user_rank
        self.assertEqual(user_rank(10), "Beginner")

    def test_user_rank_intermediate(self):
        from .views import user_rank
        self.assertEqual(user_rank(100), "Intermediate")
        self.assertEqual(user_rank(50), "Intermediate")
        self.assertEqual(user_rank(1250), "Intermediate")

    def test_user_rank_expert(self):
        from .views import user_rank
        self.assertEqual(user_rank(1300), "Expert")
        self.assertEqual(user_rank(5000), "Expert")

    def test_user_rank_boundary_conditions(self):
        from .views import user_rank
        self.assertEqual(user_rank(49), "Beginner")
        self.assertEqual(user_rank(50), "Intermediate")
        self.assertEqual(user_rank(1250), "Intermediate")
        self.assertEqual(user_rank(1251), "Expert")