from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Vacancy, VacancyView, VacancyResponse, Anketa, VacancyComplaint

User = get_user_model()


class VacancyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="password12345")
        self.vacancy = Vacancy.objects.create(
            user=self.user,
            title="Python Developer",
            description="Django dev needed",
            about_me="We are a company",
            work_type="work",
            work_time="full_time",
            salary=50000,
            country="Kyrgyzstan",
            city="Bishkek",
            requirements="Python, Django",
            responsibilities="Develop backend"
        )

    def test_vacancy_str(self):
        self.assertEqual(str(self.vacancy), "Python Developer")

    def test_get_absolute_url(self):
        url = self.vacancy.get_absolute_url()
        self.assertEqual(url, reverse("api:vacancy_detail", kwargs={"pk": self.vacancy.pk}))

    def test_get_responded_workers_empty(self):
        self.assertEqual(self.vacancy.get_responded_workers(), [])


class AnketaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="anketa@example.com", password="12345")
        self.anketa = Anketa.objects.create(
            user=self.user,
            title="Backend Dev",
            about_me="Python Django dev",
            experience="2 years",
            country="Kyrgyzstan",
            city="Bishkek",
            phone_number="+996555111222"
        )

    def test_str(self):
        self.assertIn("Backend Dev", str(self.anketa))
        self.assertIn(self.user.email, str(self.anketa))


class VacancyResponseModelTest(TestCase):
    def setUp(self):
        self.worker = User.objects.create_user(email="worker@example.com", password="password12345")
        self.owner = User.objects.create_user(email="owner@example.com", password="password12345")
        self.vacancy = Vacancy.objects.create(
            user=self.owner,
            title="Django Dev",
            description="Backend dev",
            about_me="Owner company",
            work_type="work",
            work_time="full_time",
            salary=70000,
            country="Kyrgyzstan",
            city="Bishkek",
            requirements="Django",
            responsibilities="API"
        )
        self.anketa = Anketa.objects.create(
            user=self.worker,
            title="Junior Dev",
            about_me="Some about me",
            experience="1 year",
            country="Kyrgyzstan",
            city="Osh",
            phone_number="+996555000111"
        )

    def test_unique_response(self):
        VacancyResponse.objects.create(worker=self.worker, vacancy=self.vacancy, anketa=self.anketa)
        with self.assertRaises(Exception):
            VacancyResponse.objects.create(worker=self.worker, vacancy=self.vacancy, anketa=self.anketa)


class VacancyViewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="viewer@example.com", password="password12345")
        self.owner = User.objects.create_user(email="owner2@example.com", password="password12345")
        self.vacancy = Vacancy.objects.create(
            user=self.owner,
            title="Frontend Dev",
            description="React dev",
            about_me="Frontend team",
            work_type="work",
            work_time="flexible",
            salary=60000,
            country="Kyrgyzstan",
            city="Bishkek",
            requirements="React",
            responsibilities="Frontend dev"
        )

    def test_create_view(self):
        view = VacancyView.objects.create(
            vacancy=self.vacancy,
            user=self.user,
            ip="127.0.0.1",
            action="view"
        )
        self.assertEqual(view.vacancy, self.vacancy)
        self.assertEqual(view.user, self.user)
        self.assertEqual(view.ip, "127.0.0.1")


class VacancyComplaintModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",  # обязательное поле
            password="pass123"
        )
        self.vacancy = Vacancy.objects.create(
            user=self.user,
            title="Backend Developer",
            description="Django dev",
            is_active=True,
        )

    def test_complaint_with_user(self):
        complaint = VacancyComplaint.objects.create(
            user=self.user,
            vacancy=self.vacancy,
            reason="Неправильная информация"
        )
        self.assertIn("пожаловался", str(complaint))
        self.assertIn("Backend Developer", str(complaint))

    def test_complaint_anonymous(self):
        complaint = VacancyComplaint.objects.create(
            vacancy=self.vacancy,
            reason="Спам",
            anon_name="Anon",
            anon_email="anon@example.com"
        )
        self.assertIn("Аноним пожаловался", str(complaint))
        self.assertIn("Backend Developer", str(complaint))
