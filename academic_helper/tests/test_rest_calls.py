import io
import json
from unittest import skip

from django.conf import settings
from django.test import Client
from django.test import TestCase, RequestFactory
from ics import Calendar

from academic_helper.logic.shnaton_parser import ShnatonParser
from academic_helper.management.init_data import COURSES_TO_FETCH
from academic_helper.models import CoursistUser
from academic_helper.views.schedule import ScheduleView

COURSE = COURSES_TO_FETCH[0]

urls_to_get = [
    "",
    "/courses/",
    f"/courses/{COURSE}",
    "/about/",
    "/schedule/",
    "/admin/",
    "/degree-program",
    "/health_check/",
    "/accounts/signup/",
    "/accounts/login/",
]


class TestRestCalls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_urls(self):
        settings.SOCIAL_AUTH_ACTIVATION = False
        parser = ShnatonParser()
        parser.fetch_course(COURSE)
        client = Client()
        for url in urls_to_get:
            response = client.get(url, follow=True)
            self.assertEquals(response.status_code, 200, f"Failed fetching {url}")

    def test_post_urls(self):
        pass
