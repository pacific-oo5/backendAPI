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

# Create your tests here.
