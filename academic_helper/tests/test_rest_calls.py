from django.test import Client
from django.test import TestCase

from academic_helper.management import init_data
from academic_helper.management.init_data import create_all

urls_to_get = [
    "",
    "/ajax/",
    "/courses/",
    "/courses/" + str(init_data.courses_to_fetch[0]),
    "/about/",
    "/schedule/",
    "/user/admin/",
    "/degree-program",
    "/health_check/",
    "/accounts/signup/",
    "/accounts/login/",
]


class TestRestCalls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_all()

    def test_get_urls(self):
        client = Client()
        for url in urls_to_get:
            response = client.get(url, follow=True)
            self.assertEquals(response.status_code, 200)

    def test_post_urls(self):
        pass
