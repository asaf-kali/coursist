from django.core import management
from django.test import TestCase


class TestCommands(TestCase):
    def test_dev_init(self):
        management.call_command("dev_init")
