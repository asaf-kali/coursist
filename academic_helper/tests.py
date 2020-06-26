from django.test import TestCase, SimpleTestCase
from django.urls import reverse, resolve

from academic_helper.views.basic import redirect_to_courses_view


class TestUrls(SimpleTestCase):

    def test_index(self):
        url = reverse('index')
        res = resolve(url)
        self.assertEquals(res.func, redirect_to_courses_view)


# Create your tests here.
